# Dataset Lineage

Confirmed historical flow:

`civil3-civil7 -> Dataset-30k -> added professional marine-restoration materials -> Dataset-46k -> stricter cleaning -> Dataset-16k`

Known counts:

- civil3: 4,096
- civil4: 5,762
- civil5: 6,637
- civil6: 1,872
- civil7: 21,062
- civil3-civil7 total: 39,429
- Dataset-30k: 30,890
- Dataset-46k: 46,213
- Dataset-16k: 16,631

Dataset-46k to Dataset-16k:

- 46,213 -> 44,340: basic cleaning / merging / deduplication
- 44,340 -> 21,550: marine-restoration relevance filtering
- 21,550 -> 16,631: context/template cleaning

The possible 78,350 -> 46,213 transition is not treated as fully verified unless additional original evidence is supplied.
