# services/response.py (замени/дополни)

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session

from repositories.response import ResponseRepository
from repositories.question import QuestionRepository
from domain.schemas import (
    Response as ResponseSchema,
    ResponseCreate,
    ResponseUpdate,
)
from domain.schemas import Question as QuestionSchema


JSONValue = Union[dict, list, str, int, float, bool, None]


class ResponseService:
    def __init__(self, db: Session) -> None:
        self.db: Session = db
        self.repo = ResponseRepository(db)
        self.qrepo = QuestionRepository(db)

    # ---------- public API ----------

    def create(self, payload: ResponseCreate) -> Optional[ResponseSchema]:
        question = self._get_question_or_none(payload.question_id)
        if question is None or question.version_id != payload.version_id:
            return None

        ctx = self._answers_ctx(user_id=payload.user_id, version_id=payload.version_id)
        # поместим значение «как будто уже сохранено» — для условий, смотрящих на текущий вопрос
        self._ctx_put(ctx, question, payload.response_value)

        coerced = self._coerce_and_validate(question, payload.response_value, ctx)
        return self.repo.create(
            ResponseCreate(
                user_id=payload.user_id,
                version_id=payload.version_id,
                question_id=payload.question_id,
                response_value=coerced,
            )
        )

    def update(
        self, response_id: int, payload: ResponseUpdate
    ) -> Optional[ResponseSchema]:
        current = self.repo.get(response_id)
        if current is None:
            return None

        question = self._get_question_or_none(current.question_id)
        if question is None:
            return None

        new_value = payload.response_value
        if new_value is None:
            # допускаешь ли очистку ответа? если нет — можно кинуть ValueError
            new_value = None

        ctx = self._answers_ctx(user_id=current.user_id, version_id=current.version_id)
        self._ctx_put(ctx, question, new_value)

        coerced = self._coerce_and_validate(question, new_value, ctx)
        return self.repo.update(response_id, ResponseUpdate(response_value=coerced))

    def get(self, response_id: int) -> Optional[ResponseSchema]:
        return self.repo.get(response_id)

    def get_by_user_version(
        self, user_id: int, version_id: int
    ) -> List[ResponseSchema]:
        return self.repo.get_by_user_and_version(user_id=user_id, version_id=version_id)

    def delete(self, response_id: int) -> bool:
        return self.repo.delete(response_id)

    # ---------- context of answers ----------

    def _answers_ctx(self, user_id: int, version_id: int) -> Dict[str, JSONValue]:
        """
        Собирает контекст ответов: по номеру вопроса и по id.
        Ключи вида:
          - f"id:{question_id}" -> value
          - f"num:{question.number}" -> value
        """
        ctx: Dict[str, JSONValue] = {}
        answers = self.repo.get_by_user_and_version(
            user_id=user_id, version_id=version_id
        )
        if not answers:
            return ctx
        # понадобится мапа id->question.number
        qids = [a.question_id for a in answers]
        qmap = self.qrepo.get_map_by_ids(qids)  # см. ниже добавим метод
        for a in answers:
            number = qmap.get(a.question_id)
            if number:
                ctx[f"num:{number}"] = a.response_value
            ctx[f"id:{a.question_id}"] = a.response_value
        return ctx

    @staticmethod
    def _ctx_put(
        ctx: Dict[str, JSONValue], question: QuestionSchema, value: JSONValue
    ) -> None:
        if question:
            ctx[f"id:{question.id}"] = value
            ctx[f"num:{question.number}"] = value

    # ---------- validation core ----------

    def _coerce_and_validate(
        self, question: QuestionSchema, raw_value: JSONValue, ctx: Dict[str, JSONValue]
    ) -> JSONValue:
        qtype = (question.type or "").strip().lower()
        constraints = question.constraints or {}
        options = question.options

        # 0) depends_on / condition
        self._enforce_depends_on(constraints, ctx)
        self._enforce_condition(constraints, ctx)

        # 1) типовая валидация + приведение типов
        value = self._coerce_by_type(qtype, raw_value, options, constraints)

        # 2) бизнес-правила (площади/лифты)
        self._enforce_area_rules(question, value, ctx, constraints)
        self._enforce_elevator_rules(question, value, ctx, constraints)

        return value

    # ---------- type coercion ----------

    def _coerce_by_type(
        self, qtype: str, raw: JSONValue, options, constraints
    ) -> JSONValue:
        if qtype in ("boolean", "bool"):
            return self._parse_bool(raw)

        if qtype in ("integer", "int"):
            ival = self._parse_int(raw)
            self._check_min_max(ival, constraints)
            return ival

        if qtype in ("number", "float", "decimal"):
            fval = self._parse_float(raw)
            self._check_min_max(fval, constraints)
            return fval

        if qtype in ("dropdown", "select", "choice"):
            sval = str(raw) if raw is not None else ""
            allowed = None
            if isinstance(options, dict):
                allowed = options.get("values")
            elif isinstance(options, list):
                allowed = options
            if allowed is not None and len(allowed) > 0 and sval not in allowed:
                raise ValueError(f"Value '{sval}' is not in allowed options.")
            return sval

        # text/string/unknown
        sval = "" if raw is None else str(raw)
        self._check_len(sval, constraints)
        return sval

    # ---------- rule helpers ----------

    def _enforce_depends_on(
        self, constraints: Dict[str, Any], ctx: Dict[str, JSONValue]
    ) -> None:
        dep = constraints.get("depends_on")
        if not dep:
            return
        ref_key = self._ref_key(dep, ctx)
        if ref_key is None:
            return  # нет такого вопроса в контексте — трактуем как «условие не выполняется»?
        ref_val = ctx.get(ref_key)
        allowed = dep.get("values")
        if allowed is None:
            return
        if not self._value_in(ref_val, allowed):
            raise ValueError("Question is disabled by depends_on condition.")

    def _enforce_condition(
        self, constraints: Dict[str, Any], ctx: Dict[str, JSONValue]
    ) -> None:
        cond = constraints.get("condition")
        if not cond:
            return
        left = self._resolve_ref(cond.get("left"), ctx)
        right = cond.get("right")
        op = (cond.get("op") or "==").lower()

        if op == "==":
            ok = left == right
        elif op == "!=":
            ok = left != right
        elif op == ">":
            ok = self._cmp(left, right, "gt")
        elif op == ">=":
            ok = self._cmp(left, right, "ge")
        elif op == "<":
            ok = self._cmp(left, right, "lt")
        elif op == "<=":
            ok = self._cmp(left, right, "le")
        elif op == "in":
            ok = self._value_in(left, right)
        elif op == "not_in":
            ok = not self._value_in(left, right)
        else:
            raise ValueError(f"Unsupported condition op: {op}")

        if not ok:
            raise ValueError("Condition failed.")

    def _enforce_area_rules(
        self,
        question: QuestionSchema,
        value: JSONValue,
        ctx: Dict[str, JSONValue],
        constraints: Dict[str, Any],
    ) -> None:
        # total == sum(parts)
        if "area_total_of" in constraints:
            parts_nums = constraints["area_total_of"]
            tolerance = float(constraints.get("tolerance", 0.0))
            total = self._to_float(value)
            s = 0.0
            for num in parts_nums:
                v = ctx.get(f"num:{num}")
                s += self._to_float(v)
            if abs(total - s) > tolerance:
                raise ValueError(
                    f"Area total mismatch: total={total} != sum(parts)={s} (tolerance={tolerance})"
                )

        # part <= total and sum(parts) <= total
        if "area_part_of" in constraints:
            total_num = constraints["area_part_of"]
            tolerance = float(constraints.get("tolerance", 0.0))
            part = self._to_float(value)
            total_val = ctx.get(f"num:{total_num}")
            total = self._to_float(total_val)
            if part - total > tolerance:
                raise ValueError(
                    f"Area part {part} exceeds total {total} (tolerance={tolerance})"
                )
            # если хотим жёстко проверить сумму частей ≤ total — нужно знать список всех «part_of»
            # здесь минимальная проверка: текущая часть не больше итога

    def _enforce_elevator_rules(
        self,
        question: QuestionSchema,
        value: JSONValue,
        ctx: Dict[str, JSONValue],
        constraints: Dict[str, Any],
    ) -> None:
        # floors >= min -> elevator must be true
        rule = constraints.get("requires_elevator_if")
        if rule:
            floors_num = rule.get("floors_question")
            min_floors = int(rule.get("min_floors", 5))
            elev_num = rule.get("elevator_question")
            floors = self._to_int(
                self._resolve_num_or_self(floors_num, question, value, ctx)
            )
            has_elev = self._to_bool(ctx.get(f"num:{elev_num}"))
            if floors is not None and floors >= min_floors and has_elev is False:
                raise ValueError(f"Elevator required when floors >= {min_floors}.")

        # no elevator -> floors must be <= max
        rule2 = constraints.get("no_elevator_max_floors")
        if rule2:
            floors_num = rule2.get("floors_question")
            max_no = int(rule2.get("max", 5))
            elev_num = rule2.get("elevator_question")
            floors = self._to_int(
                self._resolve_num_or_self(floors_num, question, value, ctx)
            )
            has_elev = self._to_bool(ctx.get(f"num:{elev_num}"))
            if has_elev is False and floors is not None and floors > max_no:
                raise ValueError(
                    f"Floors {floors} exceed allowed maximum {max_no} without elevator."
                )

    # ---------- tiny utils ----------

    def _get_question_or_none(self, question_id: int) -> Optional[QuestionSchema]:
        return self.qrepo.get(question_id)

    @staticmethod
    def _ref_key(ref: Dict[str, Any], ctx: Dict[str, JSONValue]) -> Optional[str]:
        if not isinstance(ref, dict):
            return None
        if "question_id" in ref:
            return f"id:{ref['question_id']}"
        if "question_number" in ref:
            return f"num:{ref['question_number']}"
        return None

    @staticmethod
    def _value_in(val: JSONValue, bag: Any) -> bool:
        if isinstance(bag, (list, tuple, set)):
            return val in bag
        return val == bag

    def _resolve_ref(self, ref: Any, ctx: Dict[str, JSONValue]) -> JSONValue:
        if isinstance(ref, dict):
            key = self._ref_key(ref, ctx)
            return ctx.get(key) if key else None
        return ref

    def _resolve_num_or_self(
        self,
        number: Optional[str],
        question: QuestionSchema,
        value: JSONValue,
        ctx: Dict[str, JSONValue],
    ) -> JSONValue:
        if number:
            return ctx.get(f"num:{number}")
        # если правило ссылается на «текущий вопрос» (например, floors) — используем его value
        return value

    @staticmethod
    def _cmp(a: Any, b: Any, op: str) -> bool:
        try:
            if op == "gt":
                return a > b
            if op == "ge":
                return a >= b
            if op == "lt":
                return a < b
            if op == "le":
                return a <= b
        except Exception:
            return False
        return False

    @staticmethod
    def _parse_bool(v) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(int(v))
        if isinstance(v, str):
            s = v.strip().lower()
            if s in ("true", "1", "yes", "y", "да"):
                return True
            if s in ("false", "0", "no", "n", "нет"):
                return False
        raise ValueError("Invalid boolean value")

    @staticmethod
    def _parse_int(v) -> int:
        if isinstance(v, int) and not isinstance(v, bool):
            return v
        try:
            return int(str(v).strip())
        except Exception:
            raise ValueError("Invalid integer value")

    @staticmethod
    def _parse_float(v) -> float:
        try:
            return float(str(v).strip())
        except Exception:
            raise ValueError("Invalid number value")

    @staticmethod
    def _to_float(v) -> float:
        if v is None:
            return 0.0
        try:
            return float(v)
        except Exception:
            return 0.0

    @staticmethod
    def _to_int(v) -> Optional[int]:
        try:
            return int(v)
        except Exception:
            return None

    @staticmethod
    def _to_bool(v) -> Optional[bool]:
        if v is None:
            return None
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(int(v))
        if isinstance(v, str):
            s = v.strip().lower()
            if s in ("true", "1", "yes", "y", "да"):
                return True
            if s in ("false", "0", "no", "n", "нет"):
                return False
        return None

    @staticmethod
    def _check_min_max(value, constraints: dict) -> None:
        if "min" in constraints and value < constraints["min"]:
            raise ValueError(f"Value {value} is below min={constraints['min']}")
        if "max" in constraints and value > constraints["max"]:
            raise ValueError(f"Value {value} is above max={constraints['max']}")

    @staticmethod
    def _check_len(s: str, constraints: dict) -> None:
        if "min_length" in constraints and len(s) < constraints["min_length"]:
            raise ValueError(
                f"Text length {len(s)} is below min_length={constraints['min_length']}"
            )
        if "max_length" in constraints and len(s) > constraints["max_length"]:
            raise ValueError(
                f"Text length {len(s)} exceeds max_length={constraints['max_length']}"
            )
