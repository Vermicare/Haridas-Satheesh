"""Fictional, in-memory authorization contract; no external connector or identity proof."""
from datetime import datetime


class ContractError(ValueError):
    pass


def _utc(value):
    if not isinstance(value, str) or not value.endswith('Z'):
        raise ContractError('UTC Z timestamp required')
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ContractError('invalid timestamp') from exc
    if dt.utcoffset() is None or dt.utcoffset().total_seconds() != 0:
        raise ContractError('non-UTC timestamp')
    return dt


def simulate_once(scenario, requested_scope, *, principal, now, consumed, trusted_principals):
    """Validate then simulate exactly one action. `consumed` is only process-local."""
    if scenario.get('synthetic') is not True:
        raise ContractError('fictional fixture required')
    decision = scenario['proposed_decision']
    grant = scenario.get('authorization')
    action = scenario['simulated_action']
    if not isinstance(grant, dict) or set(grant) != {
        'id', 'decision', 'approved_by', 'scope', 'issued_at', 'expires_at', 'nonce'
    }:
        raise ContractError('invalid grant schema')
    if not isinstance(principal, str) or principal not in trusted_principals or principal != grant['approved_by']:
        raise ContractError('principal mismatch / not trusted')
    if decision.get('requires_authorization') is not True or grant['decision'] != decision.get('id'):
        raise ContractError('decision not bound')
    if action.get('authorization') != grant['id'] or action.get('connector') != 'simulated-task-store':
        raise ContractError('action authorization/connector mismatch')
    expected_scope = decision.get('scope')
    if not isinstance(expected_scope, dict) or set(expected_scope) != {'operation', 'task', 'new_due'}:
        raise ContractError('missing machine-readable decision scope')
    if any(not isinstance(v, str) or not v.strip() for v in expected_scope.values()):
        raise ContractError('invalid scope values')
    if expected_scope['operation'] != 'update_due_date' or action.get('operation') != expected_scope['operation']:
        raise ContractError('unsupported action')
    if grant['scope'] != expected_scope or requested_scope != expected_scope:
        raise ContractError('scope escalation / changed proposal')
    evidence = {e['id']: e for e in scenario['evidence']}
    refs = decision.get('evidence')
    if not isinstance(refs, list) or not refs or any(
        key not in evidence or evidence[key].get('trusted') is not True
        or evidence[key].get('approved_by') != principal for key in refs
    ):
        raise ContractError('untrusted or unapproved evidence')
    if expected_scope['task'] != evidence['E1']['content']['task']:
        raise ContractError('task does not match trusted source')
    if not isinstance(grant['nonce'], str) or not grant['nonce'] or grant['nonce'] in consumed:
        raise ContractError('replayed or invalid nonce')
    current = _utc(now)
    issued, expires = _utc(grant['issued_at']), _utc(grant['expires_at'])
    if not issued <= current < expires:
        raise ContractError('grant not yet valid / expired')
    # Simulation only. In a real system this must be an atomic durable transaction.
    consumed.add(grant['nonce'])
    return {'synthetic': True, 'result': 'simulated-success', 'action': action['id'],
            'decision': decision['id'], 'authorization': grant['id'],
            'nonce': grant['nonce'], 'external_actions': 0}
