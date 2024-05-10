from transformers import AutoModelForSeq2SeqLM, T5TokenizerFast
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import logging

modes = {
    'scoop': [3, 10],
    'link': [2, 5]
}


def init_model():
    model_name = "sarahai/ruT5-base-summarizer"
    logging.info(f'Initializing model {model_name}')
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    return model, tokenizer


model, tokenizer = init_model()
device = torch.device("cuda")
model.to(device)


def summarize(text, mode='scoop'):
    x, y = modes[mode]
    max_length = int(len(text) / x)
    min_length = int(len(text) / y)
    input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device)
    outputs = model.generate(input_ids,
                             max_length=max_length,
                             min_length=min_length,
                             length_penalty=1,
                             num_beams=2,
                             max_new_tokens=min_length,
                             do_sample=True,
                             top_p=1,
                             top_k=10,
                             repetition_penalty=1.5,
                             no_repeat_ngram_size=2,
                             early_stopping=True)  # change according to your preferences
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary
