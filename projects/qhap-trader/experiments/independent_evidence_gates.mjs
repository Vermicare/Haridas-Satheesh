// Offline research screening only. Never authorizes replay, licensing, or broker orders.
export function assessEvidenceGates(receipt) {
  const historical = [], prospective = [];
  if (!receipt || typeof receipt !== 'object' || Array.isArray(receipt)) {
    return {historical:{status:'BLOCKED',reasons:['INVALID_RECEIPT']},prospective:{status:'BLOCKED',reasons:['INVALID_RECEIPT']},replay_authorized:false,orders_possible:false};
  }
  const fields = ['provider','instrument_isin','product_and_granularity','bar_timestamp_timezone_and_construction','license_reference_local_only','session_calendar_reference','corporate_action_reference','local_source_sha256'];
  for (const key of fields) if (typeof receipt[key] !== 'string' || !receipt[key].trim() || receipt[key].trim().toUpperCase()==='UNKNOWN') historical.push(`MISSING_${key.toUpperCase()}`);
  if (!/^[a-f\d]{64}$/i.test(receipt.local_source_sha256 ?? '')) historical.push('INVALID_SHA256');
  for (const key of ['research_non_display_permitted','retention_permitted']) if (receipt[key] !== true) historical.push(`UNVERIFIED_${key.toUpperCase()}`);
  if (typeof receipt.public_redistribution_permitted !== 'boolean') historical.push('UNKNOWN_REDISTRIBUTION_RIGHTS');
  if (!Number.isSafeInteger(receipt.unseen_historical_session_count) || receipt.unseen_historical_session_count < 60) historical.push('INSUFFICIENT_UNSEEN_HISTORICAL_SESSIONS');
  if (!Number.isSafeInteger(receipt.distinct_historical_regime_count) || receipt.distinct_historical_regime_count < 3) historical.push('INSUFFICIENT_HISTORICAL_REGIMES');
  if (receipt.parameters_frozen_before_data_access !== true) historical.push('PARAMETERS_NOT_VERIFIABLY_FROZEN');
  historical.push('INDEPENDENT_ENTITLEMENT_PROVENANCE_AND_CALENDAR_AUDIT_REQUIRED');
  if (!Number.isSafeInteger(receipt.observed_session_count) || receipt.observed_session_count < 60) prospective.push('INSUFFICIENT_PROSPECTIVE_SESSIONS');
  if (receipt.persistent_local_safety_verified !== true) prospective.push('LOCAL_SAFETY_UNVERIFIED');
  if (receipt.live_feed_event_provenance_verified !== true) prospective.push('LIVE_FEED_EVENT_PROVENANCE_UNVERIFIED');
  prospective.push('INDEPENDENT_PROSPECTIVE_SESSION_AUDIT_REQUIRED');
  return {historical:{status:'BLOCKED',reasons:historical},prospective:{status:'BLOCKED',reasons:prospective},replay_authorized:false,orders_possible:false};
}
