# Dataset card

This card follows the structure of Gebru et al. (2021), "Datasheets for Datasets". It lists every data source the swarm apps train or test on.

| App | Source | Real or generated | Period / size | License |
| :-- | :-- | :-- | :-- | :-- |
| Energy | ERCOT hourly native load (COAST zone) and NREL NSRDB weather | real | committed sample: 2020, 8,784 hours. The pipeline covers 2018-2022. | ERCOT public data; NSRDB public (NREL API key needed to download) |
| Hotel peak energy | ERCOT load as the grid signal, plus generated hotel equipment loads | mixed | summer 2020 | as above |
| Hotel housekeeping, relocation, shifts | five fictional hotels, about 640k generated bookings | generated | four years | MIT (this repository) |
| Wildfire | cellular-automaton forest with random ignition and wind | generated | one episode per seed | MIT |
| CityLearn | CityLearn Challenge 2022: 17 homes with solar and batteries | real building data, simulated batteries | one year, hourly | CityLearn license (MIT); see the CityLearn repository |
| VMAS navigation | VMAS simulator | generated | one episode per seed | VMAS license (GPL-3.0); installed as an optional extra and not redistributed here |

## How each dataset is built

- **Energy:**
  - [`apps/energy/pipeline`](../apps/energy/pipeline/README.md) downloads, cleans and merges ERCOT and NREL data hour by hour.
  - The committed sample is [`apps/energy/data/sample/ercot_nrel_2020.csv`](../apps/energy/data/sample/ercot_nrel_2020.csv), with columns timestamp, GHI, DNI, DHI, Temperature, Wind Speed and demand_mw.
- **Hotel:** [`apps/hotel/analytics`](../apps/hotel/analytics) generates the bookings. A small extract is in [`apps/hotel/data/sample`](../apps/hotel/data/sample). No real guest or employee data is used.
- **CityLearn:** `python -m apps.citylearn.download` fetches the 2022 challenge files into `data/citylearn/`, which is not committed.
- **Generated apps:** an episode is fully determined by its seed, so every test episode can be regenerated exactly.

## Splits

| App | Train | Validation | Test |
| :-- | :-- | :-- | :-- |
| Energy | Jan–Aug | Sep | Oct–Dec |
| Hotel peak energy | even ISO weeks | alternate odd weeks | remaining odd weeks |
| CityLearn | Jan–Aug | Sep | Oct–Dec |
| Generated apps | seeds 0+ | seeds 5000+ | seeds 10000+ |

The validation and test splits are never used for training. Checkpoints are chosen on validation only. See [evaluation-protocol.md](evaluation-protocol.md).

## Known gaps and biases

- **Energy:**
  - One Texas zone in one year. Load shape, weather and peak timing differ elsewhere.
  - 2020 includes the COVID-19 load dip.
  - The 2018–2022 rebuild is on hold until a new NREL key is available.
- **Generated hotels:** they reflect the generator's assumptions (seasonality, channel mix, cancellation rates), not any real property.
- **Wildfire:** the simulator ignores terrain, fuel type and real fire physics. Real Ontario fuel data (CWFIS) is planned but on hold.
