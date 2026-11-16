# Reconstruct the multi-radio bridge

This source preparation adds explicit logical networks, directional transmitters, receive-only contributors and shadow receivers. It also includes deployed packet-type policy, independent observer subscriptions and private-link pause/resume safeguards. The default policies remain opt-in; reconstructing source does not activate radios or forwarding.

The coordinated November 16, 2026 source release pins Core `4441ec7dbae819a765969caabb01ad477d526ad8` and backend `77363b225b96b2edfdf75ef32103b7305e946388` in components.current.json. Both commits were verified on their canonical kesh/bridge branches before updating this manifest. This hub revision includes the matching private_link/daemon.py and service-toggle tests. Historical components.json is unchanged.

Install the pinned sources with --no-deps as described in the hub README so the backend's inherited upstream Core dependency does not replace the matching fork. For offline checks, put the hub, Core src directory and backend directory on PYTHONPATH and load tools/bench_test_guard.py. The guard denies physical serial devices and non-loopback sockets.

Preserve the current hub adapter and transport implementation. Its validated inbound-activity diagnostics coexist with the daemon's generation guards that invalidate queued and delayed work across pause/resume. An inbound activity timestamp is not an RF delivery receipt.

Supply installation-specific configuration separately: channel secrets and mappings, identity, designated transmitter IDs, stable serial paths, TLS material, observer identities and credential-file paths. None belong in this source release. RX-only radios must never be designated physical transmitters. Shadow radios cannot cause forwarding or replies; active receiver contribution requires separate explicit enablement. Same-network receiver repeating is a separate option. Use stable physical USB paths when USB adapters have identical serial numbers.

The independent subscriber accepts verified WSS endpoints and private credential files; it does not publish. Observer status is metadata, not packet reception proof. Local exact-frame echo counters are also distinct from remote reception evidence.

The existing UI and firmware pins remain historical and unchanged in this preparation. This release does not claim to reconstruct all deployed UI assets or to flash hardware. Observer label formatting intentionally remains the canonical fork's presentation rather than copying a local deployment label. Generated version metadata is produced by packaging, not copied from an installed runtime.

The November 16 update adds a shared local-RF observation stream per network and central companion membership. MQTT consumes logical events; companions retain protocol-aware router deduplication. Additional compatible receivers join through topology configuration, without changing consumer lists; tests cover three active ears per network. Shadows stay separate and never acquire transmit ownership. See the backend [logical receiver configuration and limits](https://github.com/kesh33w/openhop_repeater/blob/77363b225b96b2edfdf75ef32103b7305e946388/docs/logical-receivers.md).

Validation: 153 focused candidate tests and 126 tests against the coordinated publication sources passed. Independent review covered implementation, rollout and publication scope. A saved capture identity/time replay matched 1,971 events from 7,253 observations; raw frames were unavailable, so this is not a protocol replay. A controlled Pi rollout verified connected receivers and natural logical observations. These pins reconstruct source, not private operational configuration.
