from registar.registar import Registar
from rrs_operator.rrs_operator import Operator


def main() -> None:
    operator = Operator()
    add_user_callback = operator.get_robonomics_add_user_callback()
    unpin_logs_from_IPFS_callback = operator.get_unpin_logs_from_IPFS_callback()
    registar = Registar(add_user_callback, unpin_logs_from_IPFS_callback)


if __name__ == "__main__":
    main()
