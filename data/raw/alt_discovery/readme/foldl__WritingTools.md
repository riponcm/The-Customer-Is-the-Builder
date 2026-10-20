

# Writing Tools

https://github.com/user-attachments/assets/00c3782f-a56d-4117-9957-26a192b64367


## 🚀 What is it?

Writing Tools, Apple's AI-inspired app, enchants Windows, enhancing your pen with AI LLMs.
One hotkey press, system-wide, fixes grammar, punctuation, and more. It's the world's most intelligent, system-wide grammar assistant.

Based on [ChatLLM.cpp](https://github.com/foldl/chatllm.cpp), and built with [Delphi](https://www.embarcadero.com/products/delphi) and [Lazarus](https://www.lazarus-ide.org/).

🚀🚀🚀 Don't forget to update ChatLLM.cpp bindings to enjoy GPU acceleration!

### 🌟 Why Choose Writing Tools?

>_In the realm of AI, a secret lies,<br/> Where LLMs run on your very site.<br/> System-wide, without a hitch,<br/> Instantly in any app you might pick._<br/>
>
>_Clipboard untouched, a pure delight,<br/> No need to worry, no data to steal.<br/> Purely native, no Python, no Java, no JS,<br/> Bloat-free, CPU usage, it's a joke._<br/>
>
>_Chat mode, a quick query's delight,<br/> No text selected, a chat mode you'll find.<br/> For quick queries, assistance at your command,<br/> All commands customizable, a true delight._<br/>
>
>_Privacy, absolute, a promise kept,<br/>No data to share, no worries to find.<br/> Free and open-source, a pure delight,<br/> Purely native, no bloat, no pain._<br/>
>
>_With OpenAI's API online, <br/>A trade-off made for access refined.<br/>In the world of AI, a secret lies,<br/> Where LLMs run on your very site._<br/>


- **_Absolute_ privacy**: Based on ChatLLM.cpp. LLMs run on your machine.
- **System-wide functionality**: Works instantly in **any application** where you can select text. **Does not overwrite your clipboard**.
- **Completely free and open-source**: Purely native. Bloat-free & uses pretty much **0% of your CPU**.
- **Chat Mode**: Seamlessly switching between context processing mode and chat mode.
- **Customization**: All commands are fully customizable.
- **Markdown/Math rendering**: Beautiful and elegant.
- **Trade-off on privacy**: Sometimes one needs to access an online even powerful models, so OpenAI compatible services are also supported.

## ✨ Features

All features are defined by users based on their own needs. Some examples.

- **Proofread**: The smartest grammar and spelling corrector.
- **Rewrite**: Improve the phrasing of your text.
- **Make Friendly/Professional**: Adjust the tone of your writing.
- **Summarize**: Create concise summaries of longer texts.
- **Create Tables**: Convert text into a structured Markdown table.
- **Custom Instructions**: Give specific directions (e.g. `Translate to Chinese`).

Invoke Writing Tools with no text selected to enter quick chat mode.

## 🛠 Quick Start

1. Go to the [Releases](https://github.com/foldl/WritingTools/releases) page and download the latest package.

1. Extract it anywhere you want.

1. To use local LLMs served by [ChatLLM.cpp](https://github.com/foldl/chatllm.cpp) for complete privacy, download a quantized model. Some small models:

   |Model name        | Size (GB)      |   Link  |
   |:----------------:|---------------:|:--------------|
   | QWen-2.5 1.5B    |      1.6       |[Link](https://modelscope.cn/api/v1/models/judd2024/chatllm_quantized_qwen2.5/repo?Revision=master&FilePath=qwen2.5-1.5b.bin)  |
   | Gemma-2 2B       |      2.8       |[Link](https://modelscope.cn/api/v1/models/judd2024/chatllm_quantized_gemma2_2b/repo?Revision=master&FilePath=gemma2-2b.bin)  |

1. Configure your profile.

   Copy `profile.json.in` to `profile.json`. Fill in the path of the quantized model file and other options (see [ChatLLM.cpp](https://github.com/foldl/chatllm.cpp)):

   To setup an local LLM, just define a list of options required by [ChatLLM.cpp](https://github.com/foldl/chatllm.cpp):

   ```js
   {
      //...
      "chatllm": {
         "default": [
            "-m",
            "path of the quantized model file",
            "-ngl", "all",      // for GPU acceleration
            "+detect-thoughts"  // detect thoughts
         ]
      },
      //...
   }
   ```

   To setup an OpenAI compatible server, just define a simple dictionary:

   ```js
   {
      //...
      "chatllm": {
         "default": {
              "url": "api for chat completion",
              "key": "....",
              "model": "..."
         }
      },
      //...
   }
   ```

   Take DeepSeek as an example:

   ```js
   {
      "url": "https://api.deepseek.com/chat/completions",
      "key": "sk-.....",
      "model": "deepseek-chat"
   }
   ```

   `profile.json` shall be encoded in **UTF-8**.

1. Start `WritingTools.exe`;

### Context-aware Assistance

1. Select any text in any application (or don't select any text to use quick chat mode).

2. Press your hotkey (Default: _Win+Shift+I_).

3. Choose an option from the popup menu or enter a custom instruction.

### Quick Chat

Select nothing in other applications and press your hotkey will enter quick chat mode. Enter a prompt and start chatting.

Even if some text is selected, you can input a prompt starting with "/chat " or "chat :" to switch to chat mode.

## ⚙　Customization

Fully customizable through `profile.json`.

### LLM

Multiple LLMs can be defined and loaded simultaneously. Each is defined as an entry in `chatllm`:

```js
{
   //...
   "chatllm": {
      "default": ...,
      "another_one": ...
   },
   //...
}
```

`default` is the default LLM for actions, which can be omitted when defining actions.

### Actions

_Actions_ are represented to users as a collection of buttons. Each action is defined as a dictionary:

```js
{
   "name": "My Action",
   "prompt": "Check this:\n\n{context}",
   "sys_prompt": "....",
   "accelerator": "p",        // optional
   "llm": "another_one",      // optional
   "ai_prefix": "...",        // optional
   "ai_suffix": "...",        // optional
   "feels_lucky": true,       // optional (true or false)
   "web_app": "..."           // optional
   "action": "show"           // optional
}
```

* `name` 