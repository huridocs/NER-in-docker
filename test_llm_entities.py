from ner_in_docker.use_cases.GetLLMEntitiesUseCase import GetLLMEntitiesUseCase

sample_text = "Barack Obama was born in Hawaii and served as the 44th President of the United States. He signed the Affordable Care Act into law in 2010. The United Nations headquarters is located in New York City."

llm_extractor = GetLLMEntitiesUseCase()

print(f"Using model: {llm_extractor.model_name}")
print(f"Ollama host: {llm_extractor.host}")
print(f"\nExtracting entities from: {sample_text}\n")

entities = llm_extractor.get_entities(sample_text)

print(f"Found {len(entities)} entities:\n")
for entity in entities:
    print(f"  - {entity.text}")
    print(f"    Type: {entity.type}")
    print(f"    Position: {entity.character_start}-{entity.character_end}")
    print()
