# Reproducibility Notes

## Learning Rate

Final public/revision learning-rate口径: `4.0e-05`.

The cleaned final training configuration copied into this repository records `learning_rate: 4.0e-05`.

If external historical exports/logs contain `5.0e-05`, those traces should be treated as historical configuration-conflict evidence, not silently rewritten as final manuscript configuration. The original private project files must remain unchanged.

## Seeds

The final training framework records seed 42. Historical split scripts did not explicitly fix the Python shuffle seed.

## Provenance

Final training JSON files do not preserve record-level source-document mapping. This repository does not create artificial record-to-document provenance.
