"""List available models on NVIDIA API."""
import os
import httpx
import asyncio


async def main():
    api_key = os.getenv("NVIDIA_API_KEY", "")
    if not api_key:
        print("错误: 未设置 NVIDIA_API_KEY 环境变量")
        return

    url = "https://integrate.api.nvidia.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    models = data.get("data", [])
    print(f"共找到 {len(models)} 个模型\n")

    # 按ID排序并打印
    for model in sorted(models, key=lambda x: x["id"]):
        model_id = model["id"]
        # 过滤出可能的gpt相关模型
        if any(k in model_id.lower() for k in ["gpt", "120b", "qwen", "llama", "mistral"]):
            print(f"  {model_id}")


if __name__ == "__main__":
    asyncio.run(main())
