import streamlit as st
import time
import requests
import base64
import json
from openai import OpenAI  # DeepSeek 使用 OpenAI 兼容的 SDK
from io import BytesIO
from PIL import Image

# --- ⚙️ CONFIGURATION ---
st.set_page_config(layout="wide", page_title="奇瑞AI研发赋能DEMO")

# --- 🔑 API KEY SETUP ---
DEEPSEEK_API_KEY = "sk-e5ee6c4e3361444eb85465ff786cb883"
STABILITY_API_KEY = "sk-GaBPGNCHoVJDvmSVc5jWbYWfwZrJ7ADcxLVoS2BEAaPyajsx"

# --- API Clients Initialization ---
if DEEPSEEK_API_KEY and DEEPSEEK_API_KEY != "sk-YOUR_DEEPSEEK_API_KEY_HERE":
    deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
else:
    deepseek_client = None

STABILITY_API_HOST = 'https://api.stability.ai'
STABILITY_ENGINE_ID = "stable-diffusion-xl-1024-v1-0"

# --- Global State and Data ---
if 'step' not in st.session_state: st.session_state.step = 0
personas_base_info = {
    "tech_adventurer": {"name": "小雅", "title": "iCAR V23 潜在用户",
                        "image": "https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=466&auto=format&fit=crop"},
    "business_elite": {"name": "李总", "title": "星纪元 ES 潜在用户",
                       "image": "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=387&auto=format&fit=crop"}
}


# --- 🤖 AI & Data Functions ---
def get_simulated_user_comments(persona_key):
    if persona_key == "tech_adventurer":
        return ["iCAR V23这方盒子造型太对我胃口了！开出去回头率超高。",
                "后备箱空间真的大，我家金毛的航空箱终于能轻松放下了，赞！#宠物友好",
                "车机系统要是能深度适配一下华为鸿蒙就好了，现在感觉有点割裂。",
                "周末开去郊外野营，轻度越野完全没问题，底盘很扎实。",
                "仪表盘的UI设计有点过于卡通了，希望能有更科技感的选项。",
                "看B站‘硬核评车’的拆解了，用料还挺实在的，有点心动。", "电池续航在市区开还行，但跑高速掉得有点快啊。",
                "朋友的小米SU7车机是真的流畅，iCAR啥时候能OTA升级一下？",
                "喜欢这种有点复古又有点赛博朋克的感觉，设计师很有想法。",
                "希望增加一个220V对外放电功能，露营的时候太需要了。"]
    elif persona_key == "business_elite":
        return ["星纪元ES的外观很大气，开去见客户很有面子。", "座椅按摩功能跑长途太舒服了，是我最喜欢的功能，没有之一。",
                "后排要是能有个小桌板就完美了，有时候需要在车上用笔记本回邮件。",
                "内饰用料很高级，Nappa皮质感不错，但新车味道稍微有点大。", "智能驾驶辅助在高速上很好用，很稳，让人放心。",
                "听商业伙伴推荐才来看的，他说比他的BBA开起来舒服。", "能耗控制得不错，对于这个尺寸的电车来说算惊喜了。",
                "中控大屏的逻辑希望能再简化一点，有些常用功能藏得比较深。",
                "空气悬挂好评，过减速带的时候很从容，高级感一下就上来了。", "希望OTA能快点更新哨兵模式，停车安全很重要。"]
    return []


# --- ⭐⭐⭐ NEW AND IMPROVED ANALYSIS FUNCTION ⭐⭐⭐ ---
def analyze_comments_with_deepseek(comments, persona_key):
    if not deepseek_client: return json.dumps({"error": "DeepSeek API Key 未配置。"})

    persona_name = "科技冒险家 (iCAR V23)" if persona_key == "tech_adventurer" else "商务新锐 (星纪元 ES)"

    system_prompt = f"""
    你是一位顶级的汽车行业市场分析师。你的任务是分析关于'{persona_name}'这个潜在用户群体的用户评论。
    请完成两项任务:
    1.  总结出一个详细的用户画像, 包含'tags', 'pain_points', 'influencers'。
    2.  根据这个用户画像, 创作一段专业、富有想象力、适合输入给AI绘画模型的英文提示词(prompt), 用于生成汽车概念图。

    请严格按照以下JSON格式输出，不要添加任何 markdown 标记(`json`字样)或额外的解释文字:
    {{
      "persona_analysis": {{
        "tags": ["一个词或短语的标签", "另一个标签"],
        "pain_points": ["用户抱怨的具体痛点1", "用户抱怨的具体痛点2"],
        "influencers": ["影响用户决策的渠道或人物1", "影响用户决策的渠道或人物2"]
      }},
      "image_prompt": "一段专业的英文AI绘画提示词, 描述车辆风格、场景和氛围..."
    }}
    """
    user_prompt = "请分析以下评论，并仅返回JSON对象：\n\n" + "\n".join(f"- {comment}" for comment in comments)

    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": f"调用 DeepSeek API 时发生错误: {e}"})


def generate_with_stability(prompt):
    # (This function remains unchanged)
    if STABILITY_API_KEY == "sk-YOUR_STABILITY_AI_API_KEY_HERE":
        st.error("Stability AI API Key 未配置。");
        return None
    try:
        response = requests.post(
            f"{STABILITY_API_HOST}/v1/generation/{STABILITY_ENGINE_ID}/text-to-image",
            headers={"Content-Type": "application/json", "Accept": "application/json",
                     "Authorization": f"Bearer {STABILITY_API_KEY}"},
            json={"text_prompts": [{"text": prompt}], "cfg_scale": 7, "height": 1024, "width": 1024, "samples": 1,
                  "steps": 30, "style_preset": "photographic"},
            timeout=90
        )
        response.raise_for_status()
        data = response.json()
        image_bytes = base64.b64decode(data["artifacts"][0]["base64"])
        return Image.open(BytesIO(image_bytes))
    except Exception as e:
        st.error(f"调用Stability AI API时发生错误: {e}");
        return None


# --- UI Functions ---
def run_step_0_intro():
    st.image("https://logos-world.net/wp-content/uploads/2021/09/Chery-Logo.png", width=200)
    st.title("智启研发，效能致胜：生成式AI赋能IPD流程DEMO")
    st.markdown("---");
    st.subheader("本DEMO将使用DeepSeek进行用户分析，使用Stability AI进行造型设计")
    api_ready = (deepseek_client is not None) and (STABILITY_API_KEY != "sk-YOUR_STABILITY_AI_API_KEY_HERE")
    if not api_ready: st.error("错误：请确保在代码顶部同时配置好DeepSeek和Stability AI的API Key！")
    if st.button("开始DEMO", type="primary", use_container_width=True, disabled=not api_ready):
        st.session_state.step = 1;
        st.rerun()


def run_step_1_aggregation():
    st.header("第一步：AI Agent 从全网聚合信息 (模拟)")
    st.markdown("AI Agent正在从海量数据源中抓取和清洗与我们产品相关的用户评论...")
    with st.spinner('正在聚合数据...'):
        time.sleep(2)
        st.session_state.aggregated_data = {"tech_adventurer": get_simulated_user_comments("tech_adventurer"),
                                            "business_elite": get_simulated_user_comments("business_elite")}
    st.success("数据聚合完毕！已获取20条高质量用户评论样本。")
    if st.button("下一步：让DeepSeek分析并生成用户画像", type="primary", use_container_width=True):
        st.session_state.step = 2;
        st.rerun()


def run_step_2_analysis_and_choice():
    st.header("第二步：DeepSeek分析聚合数据并识别核心用户群")
    with st.expander("点击查看AI正在分析的20条原始评论样本"):
        st.json(
            st.session_state.aggregated_data['tech_adventurer'] + st.session_state.aggregated_data['business_elite'])
    if 'analysis_results' not in st.session_state:
        with st.spinner("DeepSeek正在对所有评论进行深度分析和聚类..."):
            results = {}
            for persona_key, comments in st.session_state.aggregated_data.items():
                analysis_json_str = analyze_comments_with_deepseek(comments, persona_key)
                try:
                    clean_json_str = analysis_json_str.strip().replace("```json", "").replace("```", "")
                    results[persona_key] = json.loads(clean_json_str)
                except json.JSONDecodeError:
                    results[persona_key] = {"error": "AI返回的JSON格式无效", "raw_output": analysis_json_str}
            st.session_state.analysis_results = results

    st.success("AI分析完成！已识别出两大核心用户群，核心洞察如下：")

    analysis_results = st.session_state.analysis_results
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("用户群A: 科技冒险家")
            tech_result = analysis_results.get("tech_adventurer", {}).get("persona_analysis", {})
            st.markdown("**核心标签:**");
            st.write(" ".join(f"`{tag}`" for tag in tech_result.get("tags", ["分析中..."])))
            st.markdown("**主要痛点:**");
            for point in tech_result.get("pain_points", ["分析中..."]): st.write(f"- {point}")
            if st.button("选择“科技冒险家”进入下一步", use_container_width=True, key="btn_tech"):
                st.session_state.selected_persona = "tech_adventurer";
                st.session_state.step = 3;
                st.rerun()

    with col2:
        with st.container(border=True):
            st.subheader("用户群B: 商务新锐")
            biz_result = analysis_results.get("business_elite", {}).get("persona_analysis", {})
            st.markdown("**核心标签:**");
            st.write(" ".join(f"`{tag}`" for tag in biz_result.get("tags", ["分析中..."])))
            st.markdown("**主要痛点:**");
            for point in biz_result.get("pain_points", ["分析中..."]): st.write(f"- {point}")
            if st.button("选择“商务新锐”进入下一步", use_container_width=True, key="btn_biz"):
                st.session_state.selected_persona = "business_elite";
                st.session_state.step = 3;
                st.rerun()


def run_step_3_prompt_generation():
    st.header("第三步：将“用户画像”转化为“产品概念”")
    persona_key = st.session_state.selected_persona
    full_analysis_result = st.session_state.analysis_results[persona_key]

    if "error" in full_analysis_result:
        st.error(f"{full_analysis_result['error']}\n原始输出: {full_analysis_result.get('raw_output', '')}");
        return

    analysis_result = full_analysis_result.get("persona_analysis", {})
    image_prompt = full_analysis_result.get("image_prompt", "AI未能生成Prompt, 请手动输入。")

    persona_info = personas_base_info[persona_key]
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(persona_info["image"], caption=persona_info["title"], use_container_width=True)
    with col2:
        st.subheader(f"AI生成的用户画像: {persona_info['name']}")
        st.markdown(f"**深度标签:**");
        st.write(" ".join(f"`{tag}`" for tag in analysis_result.get("tags", [])))
        st.markdown(f"**<span style='color:red;'>隐性痛点:</span>**", unsafe_allow_html=True);
        for point in analysis_result.get("pain_points", []): st.info(f"💡 {point}")
        st.markdown(f"**决策影响:**");
        for influencer in analysis_result.get("influencers", []): st.success(f"🎯 {influencer}")

    st.markdown("---");
    st.subheader("DeepSeek根据用户画像，自动生成用于Stability AI的造型设计指令")

    image_type = st.radio("选择设计图类型:", ["**渲染图**", "**草图**", "**内饰图**"], horizontal=True)
    prompt_enhancers = {"**渲染图**": "photorealistic, 8k, ultra detailed, cinematic lighting.",
                        "**草图**": "concept sketch, black and white.",
                        "**内饰图**": "interior view, cockpit, dashboard."}

    # 组合AI生成的prompt和风格选择
    final_prompt = f"{image_prompt}, {prompt_enhancers[image_type]}"
    st.session_state.prompt = st.text_area("最终AI设计指令:", final_prompt, height=150)

    if st.button("🚀 点击这里，让Stability AI开始造型设计！", type="primary", use_container_width=True):
        st.session_state.step = 4;
        st.rerun()


def run_step_4_generation():
    st.header("第四步：Stability AI辅助造型设计产出")
    prompt = st.session_state.get("prompt", "")
    if not prompt: st.error("设计指令丢失，请返回重试。"); return
    st.info(f"**正在使用的设计指令:** {prompt}")
    with st.spinner('Stability AI正在进行颠覆式创新设计... 请稍候 (大约需要15-30秒)'):
        image_result = generate_with_stability(prompt)
    if image_result:
        st.success("设计概念生成完毕！");
        st.image(image_result, caption="AI生成的爆款概念车", use_container_width=True);
        st.balloons()
    else:
        st.error("图片生成失败。请检查API Key、账户余额或网络连接后重试。")
    st.markdown("---");
    st.subheader("这就是从市场噪音到爆品概念的全链路赋能！")
    if st.button("返回并尝试其他设计", use_container_width=True):
        st.session_state.step = 2;
        st.rerun()


# --- Main App Flow ---
if st.session_state.step == 0:
    run_step_0_intro()
elif st.session_state.step == 1:
    run_step_1_aggregation()
elif st.session_state.step == 2:
    run_step_2_analysis_and_choice()
elif st.session_state.step == 3:
    run_step_3_prompt_generation()
elif st.session_state.step == 4:
    run_step_4_generation()

# Sidebar Reset Button
st.sidebar.markdown("---")
if st.sidebar.button("重置DEMO"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()