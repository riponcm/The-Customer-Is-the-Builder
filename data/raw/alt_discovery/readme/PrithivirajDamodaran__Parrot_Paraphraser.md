[![PyPI - License](https://img.shields.io/hexpm/l/plug)](https://github.com/PrithivirajDamodaran/Parrot/blob/main/LICENSE)
[![visitors](https://visitor-badge.glitch.me/badge?page_id=Parrot_Paraphraser.count_visitors)](https://visitor-badge.glitch.me)

# Parrot
Parrot is a paraphrase based utterance augmentation framework purpose built to accelerate training NLU models. A paraphrase framework is more than just a paraphrasing model.

<img src="images/Logo.png" width="35%" height="35%" align="right" />

## Table of contents
- [Why Parrot?](#why-parrot-)
- [Getting started](#getting-started)
  * [Install](#install)
  * [Quickstart](#quickstart)
  * [Getting syntactic and phrasal diversity/variety in your paraphrases ?](#getting-syntactic-and-phrasal-diversity-variety-in-your-paraphrases--)
  * [Other Knobs](#other-knobs)
- [Scope](#scope)
- [What makes a paraphraser a good augmentor for NLU? (Details)](#what-makes-a-paraphraser-a-good-augmentor-for-nlu---details-)
  * [Sample NLU data (Rasa format)](#sample-nlu-data--rasa-format-)
- [Power of Augmentation - Metrics and Comparison](#power-of-augmentation---metrics-and-comparison)
- [Current Features](#current-features)
- [Roadmap](#roadmap)
- [Current Limitations/Known issues](#current-limitations-known-issues)
- [References](#references)
- [Citation](#citation)



## Why Parrot?
**Huggingface** lists [16 paraphrase generation models,](https://huggingface.co/models?pipeline_tag=text2text-generation&search=paraphrase) (as of this writing)  **RapidAPI** lists 7 fremium and commercial paraphrasers like [QuillBot](https://rapidapi.com/search/paraphrase?section=apis&page=1), Rasa has discussed an experimental paraphraser for augmenting text data [here](https://forum.rasa.com/t/paraphrasing-for-nlu-data-augmentation-experimental/27744), Sentence-transfomers offers a [paraphrase mining utility](https://www.sbert.net/examples/applications/paraphrase-mining/README.html) and [NLPAug](https://github.com/makcedward/nlpaug) offers word level augmentation with a [PPDB](http://paraphrase.org/#/download) (a multi-million paraphrase database). While these attempts at paraphrasing are great, there are still some gaps and paraphrasing is NOT yet a mainstream option for text augmentation in building NLU models....Parrot is a humble attempt to fill some of these gaps.

**What is a good paraphrase?** Almost all conditioned text generation models are validated  on 2 factors, (1) if the generated text conveys the same meaning as the original context (Adequacy) (2) if the text is fluent / grammatically correct english (Fluency). For instance Neural Machine Translation outputs are tested for Adequacy and Fluency. But [a good paraphrase](https://www.aclweb.org/anthology/D10-1090.pdf) should be adequate and fluent while being as different as possible on the surface lexical form. With respect to this definition, the  **3 key metrics** that measures the quality of paraphrases are:
 - **Adequacy** (Is the meaning preserved adequately?) 
 - **Fluency** (Is the paraphrase fluent English?) 
 - **Diversity (Lexical / Phrasal / Syntactical)** (How much has the paraphrase changed the original sentence?)

*Parrot offers knobs to control Adequacy, Fluency and Diversity as per your needs.*

**What makes a paraphraser a good augmentor?** For training a NLU model we just don't need a lot of utterances but utterances with intents and slots/entities annotated. Typical flow would be:
- Given an **input utterance  + input annotations** a good augmentor spits out N **output paraphrases** while preserving the intent and slots. 
 - The output paraphrases are then converted into annotated data using the input annotations that we got in step 1.
 - The annotated data created out of the output paraphrases then makes the training dataset for your NLU model.

But in general being a generative model paraphrasers doesn't guarantee to preserve the slots/entities. So the ability to generate high quality paraphrases in a constrained fashion without trading off the intents and slots for lexical dissimilarity makes a paraphraser a good augmentor. *More on this in section 3 below*

## Getting started
### Install
```python
pip install git+https://github.com/PrithivirajDamodaran/Parrot_Paraphraser.git
```

[*Trying to install for AMD GPUs?*](README.md#installation-for-amd-gpus)

### Demo notebook
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1oHwF5sXxLGH8i6M0YGwGP0RstwZQDuGW?usp=sharing) Demo notebook

### Quickstart
```python


from parrot import Parrot
import torch
import warnings
warnings.filterwarnings("ignore")

''' 
uncomment to get reproducable paraphrase generations
def random_state(seed):
  torch.manual_seed(seed)
  if torch.cuda.is_available():
    torch.cuda.manual_seed_all(seed)

random_state(1234)
'''

#Init models (make sure you init ONLY once if you integrate this to your code)
parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5")

phrases = ["Can you recommend some upscale restaurants in Newyork?",
           "What are the famous places we should not miss in Russia?"
]

for phrase in phrases:
  print("-"*100)
  print("Input_phrase: ", phrase)
  print("-"*100)
  para_phrases = parrot.augment(input_phrase=phrase, use_gpu=False)
  for para_phrase in para_phrases:
   print(para_phrase)
```

```
----------------------------------------------------------------------
Input_phrase: Can you recommed some upscale restaurants in Newyork?
----------------------------------------------------------------------
list some excellent restaurants to visit in new york city?
what upscale restaurants do you recommend in new york?
i want to try some upscale restaurants in new york?
recommend some upscale restaurants in newyork?
can you recommend some high end restaurants in newyork?
can you recommend some upscale restaurants in new york?
can you recommend some upscale restaurants in newyork?
-----------------------------------------