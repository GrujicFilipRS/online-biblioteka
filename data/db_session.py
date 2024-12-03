from os.path import exists
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

SqlAlchemyBase = orm.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("You need to specify the database file.")

    base_exists = exists(db_file.strip())
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Connecting to the database at {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models

    SqlAlchemyBase.metadata.create_all(engine)
    if not base_exists:
        db_session = create_session()

        admin = __all_models.users.User(nickname='admin')
        admin.set_password("lol")

        db_session.merge(admin)
        db_session.commit()
        print("commited")


def create_session() -> Session:
    global __factory
    return __factory()
