# Reconstruct the multi-radio bridge

This source preparation adds explicit logical networks, directional transmitters, receive-only contributors and shadow receivers. It also includes deployed packet-type policy, independent observer subscriptions and private-link pause/resume safeguards. The default policies remain opt-in; reconstructing source does not activate radios or forwarding.

The coordinated November 16, 2026 source release pins Core `ab887514d56009d847f5b17094079c7dc3037c57` and backend `54fe52fc3478defd1edc82f7d7ea3f5b8cd95038` in components.current.json. Both commits were verified on their canonical kesh/bridge branches before updating this manifest. This hub revision includes the matching private_link/daemon.py and service-toggle tests. Historical components.json is unchanged.

Install the pinned sources with --no-deps as described in the hub README so the backend's inherited upstream Core dependency does not replace the matching fork. For offline checks, put the hub, Core src directory and backend directory on PYTHONPATH and load tools/bench_test_guard.py. The guard denies physical serial devices and non-loopback sockets.

Preserve the current hub adapter and transport implementation. Its validated inbound-activity diagnostics coexist with the daemon's generation guards that invalidate queued and delayed work across pause/resume. An inbound activity timestamp is not an RF delivery receipt.

Supply installation-specific configuration separately: channel secrets and mappings, identity, designated transmitter IDs, stable serial paths, TLS material, observer identities and credential-file paths. None belong in this source release. RX-only radios must never be designated physical transmitters. Shadow radios cannot cause forwarding or replies; active receiver contribution requires separate explicit enablement. Same-network receiver repeating is a separate option. Use stable physical USB paths when USB adapters have identical serial numbers.

The independent subscriber accepts verified WSS endpoints and private credential files; it does not publish. Observer status is metadata, not packet reception proof. Local exact-frame echo counters are also distinct from remote reception evidence.

The existing UI and firmware pins remain historical and unchanged in this preparation. This release does not claim to reconstruct all deployed UI assets or to flash hardware. Observer software labels now match the deployed OpenHop multi-radio-bridge presentation, with the full build string retained separately. Generated version metadata is produced by packaging, not copied from an installed runtime.

The November 16 update adds a shared local-RF observation stream per network and central companion membership. MQTT consumes logical events; companions retain protocol-aware router deduplication. Additional compatible receivers join through topology configuration, without changing consumer lists; tests cover three active ears per network. Shadows stay separate and never acquire transmit ownership. See the backend [logical receiver configuration and limits](https://github.com/kesh33w/openhop_repeater/blob/54fe52fc3478defd1edc82f7d7ea3f5b8cd95038/docs/logical-receivers.md).

Validation: 153 focused candidate tests and 126 tests against the coordinated publication sources passed. Independent review covered implementation, rollout and publication scope. A saved capture identity/time replay matched 1,971 events from 7,253 observations; raw frames were unavailable, so this is not a protocol replay. A controlled Pi rollout verified connected receivers and natural logical observations. These pins reconstruct source, not private operational configuration.

The coordinated TX outcome update preserves duplicate suppression as unsuccessful/no new transmission, retains pending and uncertain destination protection, avoids pointless retries, and excludes explicit suppression from LBT failure statistics. Busy-channel retries and CAD behavior remain unchanged. The publication checkout passed 185 targeted regression tests; the deployed fix was also verified using natural traffic. Historical generic failure records are not rewritten.

The separately maintained private [Keshbot fork](https://github.com/kesh33w/keshbot-openhop/commit/a231a61b76c8f69e207c9982dacbd6137e12163f) publishes compact Folsom replies, no RSSI, and SNR only for verified direct reception. Offline command, route, web/settings and ten signal checks passed. This records the bot source version without adding it to the hub materializer. Private runtime radio settings, channels, credentials and bot configuration remain outside source publication.

Observer/diagnostic parity update: MQTT software labels preserve the deployed presentation and full software_build metadata. Private-link peer status consistently exposes last_valid_inbound_frame_age_seconds, including null for inactive peers. The matching transport/adapter activity hook is a deployment prerequisite; it records validated inbound peer activity, not RF delivery. Deploying this diagnostic must not enable a disabled link. The coordinated diagnostic/transport/service-control/observer tests passed 63 cases.

## Optional 909 MQTT fallback

These pins include ordered USB/TCP reader receipts and the optional authenticated backend receipt socket. The separate private bot commit above includes the matching client, thirty-second grace interval, late local-RF cancellation, bounded durable deduplication, approved-source health checks and qualified MQTT-origin reply. Only bare #test commands on909 are eligible;910/RAK remain excluded. Remote MQTT observations never enter bridge forwarding.

The combined publication-tree suite passed241 tests. Controlled production validation delivered27 natural RF callbacks over180seconds and passed the final receipt barrier. Source status and local proof were healthy after activation; no actual qualifying MQTT-only reply was observed in that validation. The receipt proves cancellation delivery for host-read complete frames, not absence of RF reception or firmware loss.

Private allowlists, identities, channel keys, credentials, socket secrets, runtime databases and deployment backups are intentionally excluded. Provision these separately; the feature is disabled without explicit configuration. Preserve existing MQTT connections, bridge policies and designated transmitters. Save source/config/image rollback copies and run the bot no-send validate_receipts.py helper before activation. Do not rewind durable reply claims during rollback.
