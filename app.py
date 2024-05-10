import requests
import requests
from duckduckgo_search import DDGS
from openai import OpenAI


def search_web(query: str):
    contents = []
    convs = []

    results = DDGS().text(query, max_results=10)
    for item in results:
        try:
            url = item["href"]
            response = requests.get(f"https://r.jina.ai/{url}")
            if response.status_code == 200:
                contents.append(response.text)
                convs.append(
                    {
                        "title": item["title"],
                        "url": url,
                        "body": item["body"],
                    }
                )
        except Exception as e:
            print(e)

    return contents, convs


def compose_prompt(question:str, contents:list, context_length_limit=11000):
    limit_len = context_length_limit - 2000
    if len(question) > limit_len:
        question = question[0:limit_len]

    if len(contents) > 0:
        prompts = (
            """
        您是一位由FuckPerplexity开发的大型语言人工智能助手。您将被提供一个用户问题，并需要撰写一个清晰、简洁且准确的答案。提供了一组与问题相关的上下文，每个都以[[citation:x]]这样的编号开头，x代表一个数字。请在适当的情况下在句子末尾引用上下文。答案必须正确、精确，并以专家的中立和职业语气撰写。请将答案限制在2000个标记内。不要提供与问题无关的信息，也不要重复。如果给出的上下文信息不足，请在相关主题后写上“信息缺失：”。请按照引用编号[citation:x]的格式在答案中对应部分引用上下文。如果一句话源自多个上下文，请列出所有相关的引用编号，例如[citation:3][citation:5]，不要将引用集中在最后返回，而是在答案对应部分列出。除非是代码、特定的名称或引用编号，答案的语言应与问题相同。以下是上下文的内容集：
        """
            + "\n\n"
            + "```"
        )
        ref_index = 1
        for ref_text in contents:
            prompts = (
                prompts + "\n\n" + " [citation:{}]  ".format(str(ref_index)) + ref_text
            )
            ref_index += 1

        if len(prompts) >= limit_len:
            prompts = prompts[0:limit_len]
        prompts = (
            prompts
            + """
```
记住，不要一字不差的重复上下文内容. 回答必须使用简体中文，如果回答很长，请尽量结构化、分段落总结。请按照引用编号[citation:x]的格式在答案中对应部分引用上下文。如果一句话源自多个上下文，请列出所有相关的引用编号，例如[citation:3][citation:5]，不要将引用集中在最后返回，而是在答案对应部分列出。下面是用户问题：
"""
            + question
        )
    else:
        prompts = question

    return prompts


def chat(prompt:str, api_key:str):
    llm = OpenAI(api_key=api_key)
    completion = llm.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.2,
    )
    return completion.choices[0].message.content


def main(query: str, api_key:str):
    contents, convs = search_web(query)
    prompt = compose_prompt(query, contents, context_length_limit=8000)
    answer = chat(prompt, api_key)
    return answer, convs


if __name__ == "__main__":
    question = "娃哈哈是接班人是谁？"
    answer, convs = main(question)
    print("你的问题是：")
    print(question)
    print("-" * 100)
    print("LLM回答：")
    print(answer.replace("citation:", ""))
    print("-" * 100)
    print("参考文献：")
    for index, conv in enumerate(convs):
        print(f'[{index+1}] {conv["title"]}, 网站：{conv["url"]}')
