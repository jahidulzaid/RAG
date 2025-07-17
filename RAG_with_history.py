import ollama

# Load the dataset

dataset = []
with open('dept-notices.txt', 'r') as file:
  dataset = file.readlines()
  print(f'Loaded {len(dataset)} entries')


# Implement the retrieval system

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'

# Each element in the VECTOR_DB will be a tuple (chunk, embedding)
# The embedding is a list of floats, for example: [0.1, 0.04, -0.34, 0.21, ...]
VECTOR_DB = []

def add_chunk_to_database(chunk):
  embedding = ollama.embed(model=EMBEDDING_MODEL, input=chunk)['embeddings'][0]
  VECTOR_DB.append((chunk, embedding))

for i, chunk in enumerate(dataset):
  add_chunk_to_database(chunk)
  # print(f'Added chunk {i+1}/{len(dataset)} to the database')

def cosine_similarity(a, b):
  dot_product = sum([x * y for x, y in zip(a, b)])
  norm_a = sum([x ** 2 for x in a]) ** 0.5
  norm_b = sum([x ** 2 for x in b]) ** 0.5
  return dot_product / (norm_a * norm_b)

def retrieve(query, top_n=3):
  query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]
  # temporary list to store (chunk, similarity) pairs
  similarities = []
  for chunk, embedding in VECTOR_DB:
    similarity = cosine_similarity(query_embedding, embedding)
    similarities.append((chunk, similarity))
  # sort by similarity in descending order, because higher similarity means more relevant chunks
  similarities.sort(key=lambda x: x[1], reverse=True)
  # finally, return the top N most relevant chunks
  return similarities[:top_n]

# Responses



'''
1: one input, one output
'''


# input_query = input('Ask me a question: ')
# retrieved_knowledge = retrieve(input_query)

# print('Retrieved knowledge:')
# for chunk, similarity in retrieved_knowledge:
#   print(f' - (similarity: {similarity:.2f}) {chunk}')

# instruction_prompt = f'''You are a helpful chatbot.
# Use only the following pieces of context to answer the question. Don't make up any new information:
# {'\n'.join([f' - {chunk}' for chunk, similarity in retrieved_knowledge])}
# '''
# # print(instruction_prompt)

# stream = ollama.chat(
#   model=LANGUAGE_MODEL,
#   messages=[
#     {'role': 'system', 'content': instruction_prompt},
#     {'role': 'user', 'content': input_query},
#   ],
#   stream=True,
# )

# # print the response from the llm in real-time
# print('response:')
# for chunk in stream:
#   print(chunk['message']['content'], end='', flush=True)


'''
3: remembers conversation history. Start with an empty conversation history
'''



conversation_history = [
    {'role': 'system', 'content': "You are a helpful chatbot. Only use the given context to answer. Be concise and clear. only give the answer, not the reasoning."}
]

while True:
    input_query = input('Ask me a question: ').strip()
    if input_query.lower() in ['bye', 'exit']:
        print("Chatbot session ended. Goodbye!")
        break

    # Retrieve context for the new query
    retrieved_knowledge = retrieve(input_query)

    print('\nRetrieved knowledge:')
    for chunk, similarity in retrieved_knowledge:
        print(f' - (similarity: {similarity:.2f}) {chunk}')

    # Prepare updated instruction prompt with new context
    context_text = '\n'.join([f' - {chunk}' for chunk, similarity in retrieved_knowledge])
    instruction_prompt = f'''Use only the following pieces of context to answer the question. Don't make up any new information:
{context_text}
'''

    # Add new system context for this round
    conversation_history.append({'role': 'system', 'content': instruction_prompt})
    conversation_history.append({'role': 'user', 'content': input_query})

    # Chat with Ollama
    stream = ollama.chat(
        model=LANGUAGE_MODEL,
        messages=conversation_history,
        stream=True,
    )

    # Print response and add to history
    print('\nResponse:')
    full_response = ""
    for chunk in stream:
        content = chunk['message']['content']
        print(content, end='', flush=True)
        full_response += content

    conversation_history.append({'role': 'assistant', 'content': full_response})
    print("\n")
