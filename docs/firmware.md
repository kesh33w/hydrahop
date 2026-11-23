# Firmware releases and verification

[Download releases](https://github.com/kesh33w/hydrahop/releases) for the hardware-specific merged images, checksums, and source manifests.

The [V4.3 OLED trial release](https://github.com/kesh33w/hydrahop/releases/tag/kesh-v43-oled-20261106) retains the local60 TFT repeater, observer, enrollment and iLink behavior with OLED hardware and phone setup. New installations default to two-byte paths, 60-minute local adverts and 47-hour flood adverts. It passed a complete build, exact-target preprocessing, 37 focused native tests and image/credential checks. No non-TFT device was flashed. OLED first boot, enrollment, RF delivery and recipient ACK remain unverified. The existing TFT releases and assets remain available.

The current endpoint is a trial service hosted at sacmesh.org.

> [!WARNING]
> Flash a merged image at `0x0` with a full erase. This replaces existing firmware, identity, and settings. Browser USB flashing remains unverified.

One encrypted recipient message and return ACK passed through the Pi and TFT. This bounded test does not establish endurance or field reliability.

<details>
<summary>Recorded test and build results</summary>

| Scope | Recorded result |
| --- | --- |
| Final Internet Link implementation | 191 backend tests, 26 UI tests, type checking, and a production build passed. |
| Fresh hub integration checks | 165 tests passed. |
| Focused publication checks | 42 backend checks, 17 UI checks, type checking, and a production build passed. |

These are recorded results from their respective validation runs, not a claim that every check ran against the current documentation commit. CI status is reported separately from local tests.

</details>
