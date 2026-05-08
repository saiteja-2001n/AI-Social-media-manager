import html
import streamlit as st
import json
import os
from agent import SocialMediaAgent
from dotenv import load_dotenv

load_dotenv()

# ── Local Storage ──────────────────────────────────────────
DATA_FILE = "data.json"


# ── Load Data ──────────────────────────────────────────────
def load_data():

    if os.path.exists(DATA_FILE):

        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)

        except:
            pass

    return {
        "scheduled_posts": [],
        "generated_content": []
    }


# ── Save Data ──────────────────────────────────────────────
def save_data():

    with open(DATA_FILE, "w") as f:

        json.dump(
            {
                "scheduled_posts": st.session_state.scheduled_posts,
                "generated_content": st.session_state.generated_content,
            },
            f
        )


# ── Page Config ────────────────────────────────────────────
st.set_page_config(
    page_title="Social Media Manager",
    page_icon="📱",
    layout="wide",
)


# ── Simple CSS ─────────────────────────────────────────────
st.markdown("""
<style>

/* ── Light mode (default / system light) ── */
.stApp {
    background-color: #f5f5f5;
    color: #111111;
}

.card {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
}

.post-content {
    margin-top: 12px;
    line-height: 1.7;
    white-space: pre-wrap;
    color: #1a1a1a;
    font-size: 14px;
}

/* ── Dark mode (system preference OR Streamlit dark theme) ── */
@media (prefers-color-scheme: dark) {
    .stApp {
        background-color: #111111;
        color: white;
    }

    .card {
        background-color: #1e1e1e;
        border: none;
    }

    .post-content {
        color: #f0f0f0;
    }
}

/* ── Streamlit's own dark theme class (overrides media query) ── */
[data-theme="dark"] .stApp {
    background-color: #111111;
    color: white;
}

[data-theme="dark"] .card {
    background-color: #1e1e1e;
    border: none;
}

[data-theme="dark"] .post-content {
    color: #f0f0f0;
}

/* ── Platform badges (same in both themes) ── */
.platform-badge {
    padding: 4px 10px;
    border-radius: 15px;
    font-size: 12px;
    font-weight: bold;
    color: white;
}

.badge-linkedin  { background-color: #0A66C2; }
.badge-twitter   { background-color: #1DA1F2; }
.badge-instagram { background-color: #E1306C; }
.badge-facebook  { background-color: #1877F2; }

textarea,
input {
    border-radius: 8px !important;
}

</style>
""", unsafe_allow_html=True)


# ── Session State ──────────────────────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = SocialMediaAgent()

if "data_loaded" not in st.session_state:

    data = load_data()

    st.session_state.scheduled_posts = data["scheduled_posts"]
    st.session_state.generated_content = data["generated_content"]

    st.session_state.data_loaded = True

if "last_generated" not in st.session_state:
    st.session_state.last_generated = None

agent: SocialMediaAgent = st.session_state.agent


# ── Safe Agent Wrapper ─────────────────────────────────────
def safe_agent_run(
    prompt: str,
    n8n_base: str,
    platform: str = "LinkedIn",
    tone: str = "professional",
    include_hashtags: bool = True
) -> dict:

    try:

        result = agent.run(
            prompt,
            n8n_base_url=n8n_base,
            platform=platform,
            tone=tone,
            include_hashtags=include_hashtags
        )

        if not result.get("response"):

            result["response"] = (
                "⚠️ No response generated."
            )

        return result

    except Exception as e:

        return {
            "response": f"⚠️ Error: {str(e)}",
            "tool_results": [],
            "generated_posts": [],
            "scheduled_posts": [],
        }


# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:

    st.title("📱 Social Media Manager")

    page = st.radio(
        "Navigate",
        [
            "✍️ Generate Content",
            "📅 Scheduled Posts",
            "📊 Analytics"
        ]
    )

    st.markdown("---")

    n8n_base = st.text_input(
        "n8n Base URL",
        value="https://saitejagoud.app.n8n.cloud"
    )


# ── Generate Content ───────────────────────────────────────
if page == "✍️ Generate Content":

    st.title("✍️ Generate Content")

    topic = st.text_area(
        "Topic / Brief",
        placeholder="Write about AI automation..."
    )

    platform = st.selectbox(
        "Platform",
        ["LinkedIn", "Twitter", "Instagram", "Facebook"]
    )

    tone = st.selectbox(
        "Tone",
        [
            "Professional",
            "Casual",
            "Witty",
            "Inspirational",
            "Educational"
        ]
    )

    include_hashtags = st.checkbox(
        "🏷️ Include hashtags",
        value=True
    )

    include_emojis = st.checkbox(
        "😊 Include emojis",
        value=True
    )

    if st.button("🚀 Generate Post"):

        if topic:

            with st.spinner("Generating content..."):

                prompt = (
                    f"Generate ONLY plain text content "
                    f"for a {platform} social media post "
                    f"about {topic}. "
                    f"Tone should be {tone.lower()}. "
                    f"{'Use relevant emojis naturally throughout the post.' if include_emojis else 'Do not use emojis.'} "
                    f"Make the content engaging and professional. "
                    f"Do NOT generate HTML, CSS, XML, markdown, code blocks, <div>, <span>, or formatting tags. "
                    f"Return only clean readable social media text. "
                    f"{'Include relevant hashtags at the end.' if include_hashtags else 'Do not include hashtags.'}"
                )

                result = safe_agent_run(
                    prompt,
                    n8n_base,
                    platform=platform,
                    tone=tone.lower(),
                    include_hashtags=include_hashtags
                )

            clean_content = (
                result["response"]
                .replace("<span", "")
                .replace("</span>", "")
                .replace("<div", "")
                .replace("</div>", "")
                .replace("```html", "")
                .replace("```", "")
                .strip()
            )

            st.session_state.generated_content.append({
                "platform": platform,
                "content": clean_content,
                "topic": topic,
                "tone": tone,
                "status": "Draft",
            })

            # Store last generated post in session so buttons persist
            st.session_state.last_generated = {
                "platform": platform,
                "content": clean_content,
                "topic": topic,
                "tone": tone,
            }

            save_data()

        else:
            st.warning("Please enter a topic.")

    # ── Show last generated post + action buttons ──────────
    # Rendered OUTSIDE the generate button block so buttons persist
    if "last_generated" in st.session_state and st.session_state.last_generated:

        post = st.session_state.last_generated

        st.success("✅ Post generated and saved as draft!")

        st.markdown(
            f"""
            <div class="card">
                <span class="platform-badge badge-{post['platform'].lower()}">
                    {post['platform']}
                </span>
                <p class="post-content">{html.escape(post['content']).replace(chr(10), "<br>")}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:
            if st.button("📅 Schedule", key="schedule_last"):
                st.session_state.scheduled_posts.append({
                    **post,
                    "status": "Scheduled",
                })
                save_data()
                st.session_state.last_generated = None
                st.success("✅ Added to Scheduled Posts!")
                st.rerun()

        with c2:
            if st.button("🗑️ Delete Draft", key="delete_last"):
                # Remove last item from generated_content
                if st.session_state.generated_content:
                    st.session_state.generated_content.pop()
                save_data()
                st.session_state.last_generated = None
                st.rerun()


# ── Scheduled Posts ────────────────────────────────────────
elif page == "📅 Scheduled Posts":

    st.title("📅 Scheduled Posts")

    if not st.session_state.scheduled_posts:

        st.info("No scheduled posts available.")

    else:

        for i, post in enumerate(
            st.session_state.scheduled_posts
        ):

            badge_cls = f"badge-{post['platform'].lower()}"

            safe_content = html.escape(
                post["content"]
            ).replace("\n", "<br>")

            st.markdown(
                f"""
                <div class="card">
                    <span class="platform-badge {badge_cls}">
                        {post['platform']}
                    </span>
                    <p style="margin-top:10px; font-size:13px; color:#aaa;">
                        Status: <b style="color:#fff;">{post.get('status', 'Scheduled')}</b>
                    </p>
                    <p class="post-content">{safe_content}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns([2, 1, 1])

            with c1:

                sched_time = st.text_input(
                    "Schedule Time",
                    placeholder="2026-05-10 09:00",
                    key=f"time_{i}"
                )

            with c2:

                if st.button(
                    "📤 Publish",
                    key=f"pub_{i}"
                ):

                    with st.spinner("Sending to n8n..."):

                        result = agent.tools.trigger_n8n_schedule(
                            content=post["content"],
                            platform=post["platform"],
                            schedule_time=sched_time or "now",
                            n8n_base_url=n8n_base,
                        )

                    if result and result.get("success", True):

                        st.session_state.scheduled_posts[i]["status"] = "Published"

                        save_data()

                        st.success("✅ Published!")

                        if "execution_log" in result:

                            with st.expander("⚙️ Execution Details"):

                                st.json(
                                    result["execution_log"]
                                )

                    else:

                        st.error("❌ n8n execution failed")

            with c3:

                if st.button(
                    "🗑️ Remove",
                    key=f"remove_{i}"
                ):

                    st.session_state.scheduled_posts.pop(i)

                    save_data()

                    st.rerun()


# ── Analytics ──────────────────────────────────────────────
elif page == "📊 Analytics":

    st.title("📊 Analytics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Drafts",
        len(st.session_state.generated_content)
    )

    col2.metric(
        "Scheduled",
        len(st.session_state.scheduled_posts)
    )

    col3.metric(
        "Published",
        sum(
            1 for p in st.session_state.scheduled_posts
            if p.get("status") == "Published"
        )
    )

    st.markdown("---")

    platform_sel = st.selectbox(
        "Select Platform",
        ["LinkedIn", "Twitter", "Instagram", "Facebook"]
    )

    if st.button("📥 Fetch Analytics"):

        with st.spinner("Fetching analytics..."):

            data = agent.tools.fetch_analytics(
                platform=platform_sel,
                n8n_base_url=n8n_base
            )

        if data:

            st.markdown(f"### 📈 {platform_sel} Analytics")

            # ── Metric cards ───────────────────────────────
            METRIC_ICONS = {
                "impressions":      ("👁️", "Impressions"),
                "likes":            ("👍", "Likes"),
                "comments":         ("💬", "Comments"),
                "shares":           ("🔁", "Shares"),
                "engagement_rate":  ("⚡", "Engagement Rate"),
                "reach":            ("📡", "Reach"),
                "clicks":           ("🖱️", "Clicks"),
                "followers":        ("👥", "Followers"),
                "saves":            ("🔖", "Saves"),
                "views":            ("▶️", "Views"),
                "profile_visits":   ("🏠", "Profile Visits"),
            }

            # Pull only known metric keys (skip platform, ai_insights etc.)
            metric_keys = [
                k for k in data
                if k in METRIC_ICONS
            ]

            if metric_keys:

                cols = st.columns(len(metric_keys))

                for col, key in zip(cols, metric_keys):
                    icon, label = METRIC_ICONS[key]
                    value = data[key]
                    display = (
                        f"{value:,}" if isinstance(value, int)
                        else str(value)
                    )
                    with col:
                        st.markdown(
                            f"""
                            <div class="card" style="text-align:center; padding:20px;">
                                <div style="font-size:32px;">{icon}</div>
                                <div style="font-size:24px; font-weight:bold;
                                            color:#fff; margin:8px 0;">
                                    {display}
                                </div>
                                <div style="font-size:13px; color:#aaa;">{label}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            else:
                st.warning("No metric fields found in the n8n response.")

            # ── AI Insights ────────────────────────────────
            if data.get("ai_insights"):
                st.markdown("### 🤖 AI Insights")
                st.markdown(
                    f"""
                    <div class="card">
                        <p style="line-height:1.8; color:#f0f0f0; font-size:14px;">
                            {html.escape(str(data["ai_insights"])).replace(chr(10), "<br>")}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ── Raw response collapsible ───────────────────
            with st.expander("🔍 Raw Response"):
                st.json(data)

        else:

            st.warning("No analytics data found.")