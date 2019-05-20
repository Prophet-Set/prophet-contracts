OntCversion = '2.0.0'
from ontology.interop.Ontology.Native import Invoke
from ontology.builtins import state
from ontology.interop.System.Runtime import Notify, CheckWitness
from ontology.interop.System.ExecutionEngine import GetExecutingScriptHash
from ontology.interop.Ontology.Runtime import Base58ToAddress
from ontology.interop.System.Action import RegisterAction

# ONT Big endian Script Hash: 0x0100000000000000000000000000000000000000
OntContract = Base58ToAddress("AFmseVrdL9f9oyCzZefL9tG6UbvhUMqNMV")
# ONG Big endian Script Hash: 0x0200000000000000000000000000000000000000
OngContract = Base58ToAddress("AFmseVrdL9f9oyCzZefL9tG6UbvhfRZMHJ")

Admin = Base58ToAddress('ALcLT1nScAAnjhwWLhkCuVXhi8rbXgtpcj')

TransferEvent = RegisterAction("prophetTransfer", "from", "from_id", "to", "to_id", "amount", "currency_name")
RechargeEvent = RegisterAction("prophetRecharge", "from", "from_id", "amount")
WithdrawEvent = RegisterAction("prophetWithdraw", "to", "to_id", "amount")

def Main(operation, args):
    if operation == "transfer":
        if len(args) != 6:
            Notify("wrong params")
            return
        return transfer(args[0], args[1], args[2], args[3], args[4], args[5])
    if operation == "recharge":
        if len(args) != 3:
            Notify("wrong params")
            return
        return recharge(args[0], args[1], args[2])
    if operation == "withdraw":
        if len(args) != 3:
            Notify("wrong params")
            return
        return withdraw(args[0], args[1], args[2])
    return False

def transfer(from_acct, from_id, to_acct, to_id, ont, ong):
    param = state(from_acct, to_acct, ont)
    res = Invoke(0, OntContract, "transfer", [param])
    if res != b'\x01':
        raise Exception("transfer ont error.")
    TransferEvent(from_acct, from_id, to_acct, to_id, ont, "ont")

    param = state(from_acct, to_acct, ong)
    res = Invoke(0, OngContract, "transfer", [param])

    if res and res == b'\x01':
        TransferEvent(from_acct, from_id, to_acct, to_id, ong, "ong")
        return True
    else:
        return False

def recharge(from_acct, from_id, ongAmount):
    selfContractAddress = GetExecutingScriptHash()
    param = state(from_acct, selfContractAddress, ongAmount)
    res = Invoke(0, OngContract, 'transfer', [param])
    if res and res == b'\x01':
        RechargeEvent(from_acct, from_id, ongAmount)
        return True
    else:
        return False

def withdraw(to_acct, to_id, ongAmount):
    require(CheckWitness(Admin), "not admin")
    selfContractAddress = GetExecutingScriptHash()
    param = state(selfContractAddress, to_acct, ongAmount)
    res = Invoke(0, OngContract, 'transfer', [param])
    if res and res == b'\x01':
        WithdrawEvent(to_acct, to_id, ongAmount)
        return True
    else:
        return False

def require(condition, msg):
    if not condition:
        raise Exception(msg)
    return True

