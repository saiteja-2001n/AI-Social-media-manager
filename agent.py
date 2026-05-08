import os
import json
import requests
from tools import SocialMediaTools


class SocialMediaAgent:
    def __init__(self):
        self.tools = SocialMediaTools()
        self.n8n_base_url = "https://saitejagoud.app.n8n.cloud"

    def run(
        self,
        user_message: str,
        n8n_base_url: str = "https://saitejagoud.app.n8n.cloud",
        platform: str = "LinkedIn",
        tone: str = "professional",
        include_hashtags: bool = True,
    ) -> dict:

        self.n8n_base_url = n8n_base_url
        tool_results_log = []
        generated_posts = []
        scheduled_posts = []
        final_text = ""

        # ✅ Generate post via n8n with correct platform and tone
        if any(word in user_message.lower() for word in ["post", "write", "generate", "create"]):
            result = self.tools.generate_post(
                topic=user_message,
                platform=platform,
                tone=tone,
                include_hashtags=include_hashtags,
                n8n_base_url=n8n_base_url,
            )

            tool_results_log.append({
                "tool": "generate_post",
                "input": user_message,
                "result": result,
            })

            if result and "content" in result:
                final_text = result["content"]
            elif result and "output" in result:
                final_text = result["output"]
            elif result:
                final_text = str(result)
            else:
                final_text = "⚠️ Could not generate post. Please check n8n is active."

        # ✅ Schedule post via n8n
        elif "schedule" in user_message.lower():
            result = self.tools.trigger_n8n_schedule(
                content=user_message,
                platform=platform,
                schedule_time="now",
                n8n_base_url=n8n_base_url,
            )

            tool_results_log.append({
                "tool": "schedule_post",
                "input": user_message,
                "result": result,
            })

            final_text = "✅ Post scheduled via n8n successfully!" if result else "⚠️ Scheduling failed."

        # ✅ Analytics via n8n
        elif "analytics" in user_message.lower() or "performance" in user_message.lower():
            result = self.tools.fetch_analytics(
                platform=platform,
                n8n_base_url=n8n_base_url,
            )

            tool_results_log.append({
                "tool": "fetch_analytics",
                "input": user_message,
                "result": result,
            })

            if result:
                final_text = (
                    f"📊 Analytics for {result.get('platform', platform)}:\n"
                    f"- Impressions: {result.get('impressions', 'N/A')}\n"
                    f"- Likes: {result.get('likes', 'N/A')}\n"
                    f"- Comments: {result.get('comments', 'N/A')}\n"
                    f"- Shares: {result.get('shares', 'N/A')}\n"
                    f"- Engagement Rate: {result.get('engagement_rate', 'N/A')}\n\n"
                    f"💡 Insights: {result.get('ai_insights', 'N/A')}"
                )
            else:
                final_text = "⚠️ Could not fetch analytics. Please check n8n is active."

        else:
            result = self.tools.generate_post(
                topic=user_message,
                platform=platform,
                tone=tone,
                include_hashtags=include_hashtags,
                n8n_base_url=n8n_base_url,
            )
            if result and "content" in result:
                final_text = result["content"]
            else:
                final_text = "I can help you generate posts, schedule content, or fetch analytics. What would you like to do?"

        return {
            "response": final_text,
            "tool_results": tool_results_log,
            "generated_posts": generated_posts,
            "scheduled_posts": scheduled_posts,
        }

    # ── Tool dispatcher ───────────────────────────────────────────────────────
    def _call_tool(self, tool_name: str, tool_input: dict, n8n_base_url: str) -> dict:
        if tool_name == "generate_post":
            return self.tools.generate_post(
                topic=tool_input.get("topic", ""),
                platform=tool_input.get("platform", "LinkedIn"),
                tone=tool_input.get("tone", "professional"),
                include_hashtags=tool_input.get("include_hashtags", True),
                n8n_base_url=n8n_base_url,
            )
        elif tool_name == "schedule_post":
            success = self.tools.trigger_n8n_schedule(
                content=tool_input.get("content", ""),
                platform=tool_input.get("platform", ""),
                schedule_time=tool_input.get("schedule_time", "now"),
                n8n_base_url=n8n_base_url,
            )
            return {"success": success}
        elif tool_name == "fetch_analytics":
            return self.tools.fetch_analytics(
                platform=tool_input.get("platform", "LinkedIn"),
                date_range=tool_input.get("date_range", "last_7_days"),
                n8n_base_url=n8n_base_url,
            )
        elif tool_name == "get_scheduled_posts":
            posts = self.tools.get_scheduled_posts(n8n_base_url=n8n_base_url)
            return {"posts": posts}
        else:
            return {"error": f"Unknown tool: {tool_name}"}