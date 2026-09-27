# Workflow

The historical workflow was: professional sources -> manual collection/categorization -> Doubao-assisted source screening and organization -> document standardization -> Easy Dataset -> local DeepSeek-R1-7B -> instruction-response records -> post-generation screening and cleaning -> Dataset-30k / Dataset-46k / Dataset-16k -> LoRA fine-tuning -> evaluation -> final MER-LLM.

Doubao was used for upstream source screening/organization assistance, not as the final QA generation engine. The instruction-response corpus was generated through Easy Dataset using local DeepSeek-R1-7B and then screened/cleaned.
