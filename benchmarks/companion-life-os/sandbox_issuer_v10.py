"""Fictional issuer-signed sandbox boundary; no human authentication or real actions.

HMAC keys are shared by test issuer and verifier, so the verifier can forge tokens.
Keys used by the tests are public and MUST NOT be reused for any real account.
The harness supplies the clock; this is NOT trusted time or production consent.
"""
import base64
import hashlib
import hmac
import json

from authorization_guard_v02 import ContractError, _utc

AUDIENCE = 'fictional-companion-task-store-v1'


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def _decode_json_unique(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ContractError('duplicate signed claim')
            result[key] = value
        return result
    try:
        return json.loads(raw.decode('ascii'), object_pairs_hook=unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
    except (UnicodeError, ValueError, TypeError) as exc:
        raise ContractError('malformed signed claims') from exc


def _b64(data):
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')


def _unb64(data):
    if not isinstance(data, str) or not data or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_' for c in data):
        raise ContractError('invalid base64url token')
    try:
        decoded = base64.urlsafe_b64decode(data + '=' * (-len(data) % 4))
    except (ValueError, base64.binascii.Error) as exc:
        raise ContractError('invalid base64url token') from exc
    if _b64(decoded) != data:
        raise ContractError('noncanonical token encoding')
    return decoded


def _require_key(key):
    if not isinstance(key, bytes) or len(key) < 16:
        raise ValueError('sandbox key must be at least 16 bytes')


def _sign(claims, key):
    _require_key(key)
    body = _b64(_canonical(claims))
    signature = hmac.new(key, body.encode('ascii'), hashlib.sha256).digest()
    return body + '.' + _b64(signature)


def _verify(token, key, expected_kind, expected_keys):
    _require_key(key)
    if not isinstance(token, str) or token.count('.') != 1:
        raise ContractError('malformed signed token')
    body, signature = token.split('.')
    actual = _unb64(signature)
    expected = hmac.new(key, body.encode('ascii'), hashlib.sha256).digest()
    if not hmac.compare_digest(actual, expected):
        raise ContractError('invalid issuer signature')
    claims = _decode_json_unique(_unb64(body))
    if not isinstance(claims, dict) or set(claims) != expected_keys:
        raise ContractError('invalid signed claim schema')
    if _canonical(claims) != _unb64(body):
        raise ContractError('noncanonical signed claims')
    if claims['kind'] != expected_kind or claims['audience'] != AUDIENCE:
        raise ContractError('wrong token kind or audience')
    return claims


def _time_gate(claims, now):
    current = _utc(now)
    if not _utc(claims['issued_at']) <= current < _utc(claims['expires_at']):
        raise ContractError('signed token not yet valid or expired')


IDENTITY_KEYS = {'kind', 'audience', 'subject', 'issued_at', 'expires_at'}
APPROVAL_KEYS = {'kind', 'audience', 'principal', 'scenario_sha256', 'decision_id',
                 'scope', 'connector', 'nonce', 'issued_at', 'expires_at'}


class FictionalIssuer:
    """Test-harness fixture issuer. issue_identity does NOT authenticate a human."""
    def __init__(self, identity_key, approval_key):
        _require_key(identity_key)
        _require_key(approval_key)
        if hmac.compare_digest(identity_key, approval_key):
            raise ValueError('use distinct fictional signing keys')
        self.identity_key = identity_key
        self.approval_key = approval_key

    def issue_identity(self, subject, issued_at, expires_at):
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError('invalid fictional subject')
        if not _utc(issued_at) < _utc(expires_at):
            raise ValueError('invalid identity window')
        return _sign({'kind': 'identity', 'audience': AUDIENCE, 'subject': subject,
                      'issued_at': issued_at, 'expires_at': expires_at}, self.identity_key)

    def issue_approval(self, scenario):
        if not isinstance(scenario, dict) or scenario.get('synthetic') is not True:
            raise ValueError('fictional scenario required')
        grant = scenario.get('authorization')
        decision = scenario.get('proposed_decision')
        action = scenario.get('simulated_action')
        if not isinstance(grant, dict) or not isinstance(decision, dict) or not isinstance(action, dict):
            raise ValueError('malformed fictional approval fixture')
        if not _utc(grant['issued_at']) < _utc(grant['expires_at']):
            raise ValueError('invalid approval window')
        return _sign({'kind': 'approval', 'audience': AUDIENCE,
                      'principal': grant['approved_by'], 'scenario_sha256': hashlib.sha256(_canonical(scenario)).hexdigest(),
                      'decision_id': decision['id'], 'scope': grant['scope'],
                      'connector': action['connector'], 'nonce': grant['nonce'],
                      'issued_at': grant['issued_at'], 'expires_at': grant['expires_at']}, self.approval_key)


class FictionalSignedBoundary:
    """Verify fictional issuer attestations BEFORE invoking the existing SQLite store."""
    def __init__(self, identity_key, approval_key):
        _require_key(identity_key)
        _require_key(approval_key)
        if hmac.compare_digest(identity_key, approval_key):
            raise ValueError('keys must be distinct')
        self.identity_key = identity_key
        self.approval_key = approval_key

    def execute(self, store, scenario, requested_scope, *, identity_token, approval_token, now):
        identity = _verify(identity_token, self.identity_key, 'identity', IDENTITY_KEYS)
        approval = _verify(approval_token, self.approval_key, 'approval', APPROVAL_KEYS)
        _time_gate(identity, now)
        _time_gate(approval, now)
        if not isinstance(scenario, dict) or scenario.get('synthetic') is not True:
            raise ContractError('fictional scenario required')
        grant = scenario.get('authorization')
        decision = scenario.get('proposed_decision')
        action = scenario.get('simulated_action')
        if not all(isinstance(x, dict) for x in (grant, decision, action)):
            raise ContractError('malformed scenario')
        if not isinstance(identity['subject'], str) or not identity['subject'].strip():
            raise ContractError('invalid signed identity')
        if identity['subject'] != approval['principal'] or identity['subject'] != grant.get('approved_by'):
            raise ContractError('signed identity/approval mismatch')
        if (approval['scenario_sha256'] != hashlib.sha256(_canonical(scenario)).hexdigest()
            or approval['decision_id'] != decision.get('id')
            or approval['scope'] != grant.get('scope')
            or approval['scope'] != requested_scope
            or approval['connector'] != action.get('connector')
            or approval['nonce'] != grant.get('nonce')
            or approval['issued_at'] != grant.get('issued_at')
            or approval['expires_at'] != grant.get('expires_at')):
            raise ContractError('signed approval not bound to exact fictional action')
        # The original v0.3 store remains the sole durable nonce/receipt authority.
        # No caller-supplied principal or trusted_principals is accepted here.
        return store.execute(scenario, requested_scope, principal=identity['subject'],
                             now=now, trusted_principals={identity['subject']})
