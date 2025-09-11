import sys, pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import json
from pathlib import Path
from sqlalchemy import text
from db.database import SessionLocal


def load_payload():
    root = Path(__file__).resolve().parents[1]  # корень проекта
    with open(root / "data" / "questions_v1.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_or_create_version(db, version_name: str) -> int:
    """
    Возвращает id версии с именем `version_name`, создаёт её при отсутствии.
    Работает и на SQLite, и на PostgreSQL.
    """
    dialect = db.bind.dialect.name

    if dialect == "sqlite":
        db.execute(
            text(
                """
                INSERT INTO versions (name, created_at)
                SELECT :name, CURRENT_TIMESTAMP
                WHERE NOT EXISTS (SELECT 1 FROM versions WHERE name = :name)
            """
            ),
            {"name": version_name},
        )
        vid = db.execute(
            text("SELECT id FROM versions WHERE name = :name"),
            {"name": version_name},
        ).scalar()
        return vid
    else:
        vid = db.execute(
            text(
                """
                WITH ins AS (
                  INSERT INTO versions (name, created_at)
                  SELECT :name, NOW()
                  WHERE NOT EXISTS (SELECT 1 FROM versions WHERE name = :name)
                  RETURNING id
                )
                SELECT id FROM ins
                UNION ALL
                SELECT id FROM versions WHERE name = :name
                LIMIT 1
            """
            ),
            {"name": version_name},
        ).scalar()
        return vid


def main():
    payload = load_payload()
    version_name = payload["version"]["name"]
    questions = payload["questions"]

    db = SessionLocal()
    try:
        # 👇 заменили блок на функцию
        version_id = get_or_create_version(db, version_name)

        for q in questions:
            db.execute(
                text(
                    """
                    INSERT INTO questions (version_id, number, text, type, options, constraints)
                    SELECT :version_id, :number, :text, :type, :options, :constraints
                    WHERE NOT EXISTS (
                      SELECT 1 FROM questions WHERE version_id = :version_id AND number = :number
                    )
                """
                ),
                {
                    "version_id": version_id,
                    "number": q["number"],
                    "text": q["text"],
                    "type": q["type"],
                    "options": (
                        json.dumps(q["options"])
                        if q.get("options") is not None
                        else None
                    ),
                    "constraints": (
                        json.dumps(q["constraints"])
                        if q.get("constraints") is not None
                        else None
                    ),
                },
            )
        db.commit()
        print(f"Seed OK: version '{version_name}', questions: {len(questions)}")
    except:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
