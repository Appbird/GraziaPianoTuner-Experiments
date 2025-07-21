from typing import TypeVar
from returns.result import Success, Failure
from returns.result import Result as ActualResult

T = TypeVar("T")
E = TypeVar("E")
SimplifiedResult = Success[T] | Failure[E]
def aperture(result:ActualResult[T, E]) -> SimplifiedResult[T, E]:
    match result:
        case Failure(_) as f: return f
        case Success(_) as s: return s
    assert False, "the Result type has state other than Success and Failure."

T1 = TypeVar("T1")
T2 = TypeVar("T2")
def unify(result1:ActualResult[T1, E], result2:ActualResult[T2, E]) -> SimplifiedResult[tuple[T1, T2], E]:
    result1 = aperture(result1)
    result2 = aperture(result2)
    match result1:
        case Failure(_) as f: return f
        case Success(succ1):
            match result2:
                case Failure(_) as f: return f
                case Success(succ2):
                    return Success((succ1, succ2))

T1 = TypeVar("T1")
T2 = TypeVar("T2")
def all(results:list[ActualResult[T, E]]) -> SimplifiedResult[list[T], E]:
    results = [aperture(result) for result in results]
    unwrapped:list[T] = []
    for result in results:
        match result:
            case Failure(_) as f: return f
            case Success(succ): unwrapped.append(succ)
    return Success(unwrapped)
    