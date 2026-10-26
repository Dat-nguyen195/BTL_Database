"""Deterministic faults test caller transaction ownership; DB concurrency is separate."""
from unittest.mock import MagicMock
import pytest
from mysql.connector import Error
from src.errors import AppError,TxRetryExhaustedError
from src.services import transaction

@pytest.mark.parametrize('errno',[1213,1205])
def test_transaction_retry_success_on_second_attempt(monkeypatch,errno):
    connections=[MagicMock(),MagicMock()]
    monkeypatch.setattr(transaction,'get_db_connection',MagicMock(side_effect=connections))
    monkeypatch.setattr(transaction.time,'sleep',lambda _:None)
    action=MagicMock(side_effect=[Error(errno=errno,msg='lock conflict'),'SUCCESS'])
    assert transaction.run_in_transaction(action)=='SUCCESS'
    connections[0].rollback.assert_called_once()
    connections[0].commit.assert_not_called()
    connections[1].commit.assert_called_once()
    for conn in connections:conn.close.assert_called_once()

@pytest.mark.parametrize('errno',[1213,1205])
def test_transaction_retry_exhausted(monkeypatch,errno):
    connections=[MagicMock() for _ in range(3)]
    monkeypatch.setattr(transaction,'get_db_connection',MagicMock(side_effect=connections))
    monkeypatch.setattr(transaction.time,'sleep',lambda _:None)
    action=MagicMock(side_effect=Error(errno=errno,msg='lock conflict'))
    with pytest.raises(TxRetryExhaustedError):transaction.run_in_transaction(action)
    assert action.call_count==3
    for conn in connections:
        conn.rollback.assert_called_once()
        conn.commit.assert_not_called()
        conn.close.assert_called_once()

def test_business_error_not_retried(monkeypatch):
    conn=MagicMock()
    factory=MagicMock(return_value=conn)
    monkeypatch.setattr(transaction,'get_db_connection',factory)
    action=MagicMock(side_effect=Error(errno=60006,msg='INSUFFICIENT_FUNDS'))
    with pytest.raises(AppError) as error:transaction.run_in_transaction(action)
    assert error.value.code=='INSUFFICIENT_FUNDS'
    factory.assert_called_once()
    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()

def test_result_read_error_propagates():
    cursor=MagicMock()
    cursor.stored_results.side_effect=Error(errno=2013,msg='lost connection')
    with pytest.raises(Error):transaction.consume_call_results(cursor)

def test_commit_failure_never_returns_success(monkeypatch):
    conn=MagicMock()
    conn.commit.side_effect=Error(errno=2013,msg='lost after commit')
    monkeypatch.setattr(transaction,'get_db_connection',lambda:conn)
    with pytest.raises(AppError) as error:transaction.run_in_transaction(lambda _: 'success')
    assert error.value.code=='DATABASE_UNAVAILABLE'
    conn.rollback.assert_called_once()
