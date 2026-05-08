# tools.py

import requests
import json
from datetime import datetime


class SocialMediaTools:
    """
    All tool functions the Claude agent can call.
    Each function sends an HTTP request to an n8n webhook.
    n8n does the actual work (posting to Twitter, LinkedIn, etc.)
    """

    # ── Content Generation Tool ───────────────────────────────────────────────
    def generate_post(
        self,
        topic: str,
        platform: str,
        tone: str = "professional",
        include_hashtags: bool = True,
        n8n_base_url: str = "https://saitejagoud.app.n8n.cloud",
    ) -> dict:

        payload = {
            "message": (
                f"Generate a {tone} {platform} post about: {topic}. "
                f"{'Include relevant hashtags.' if include_hashtags else 'No hashtags.'}"
            ),
            "action": "generate_post",
            "topic": topic,
            "platform": platform,
            "tone": tone,
            "include_hashtags": include_hashtags,
            "timestamp": datetime.now().isoformat(),
        }

        return self._post(f"{n8n_base_url}/webhook/generate-post", payload)

    # ── Schedule Post Tool ────────────────────────────────────────────────────
    def trigger_n8n_schedule(
        self,
        content: str,
        platform: str,
        schedule_time: str,
        n8n_base_url: str = "https://saitejagoud.app.n8n.cloud",
    ) -> dict:

        payload = {
            "message": f"Schedule this {platform} post for {schedule_time}: {content}",
            "action": "schedule_post",
            "content": content,
            "platform": platform.lower(),
            "schedule_time": schedule_time,
            "timestamp": datetime.now().isoformat(),
        }

        result = self._post(
            f"{n8n_base_url}/webhook/schedule-post",
            payload
        )

        return result

    # ── Fetch Analytics Tool ──────────────────────────────────────────────────
    def fetch_analytics(
        self,
        platform: str,
        date_range: str = "last_7_days",
        n8n_base_url: str = "https://saitejagoud.app.n8n.cloud",
    ) -> dict:

        payload = {
            "message": f"Fetch and analyze analytics for {platform} over {date_range}.",
            "action": "fetch_analytics",
            "platform": platform.lower(),
            "date_range": date_range,
            "timestamp": datetime.now().isoformat(),
        }

        return self._post(f"{n8n_base_url}/webhook/get-analytics", payload)

    # ── Approve & Publish Tool ────────────────────────────────────────────────
    def approve_and_publish(
        self,
        post_id: str,
        n8n_base_url: str = "https://saitejagoud.app.n8n.cloud",
    ) -> dict:

        payload = {
            "message": f"Approve and publish post with ID: {post_id}",
            "action": "approve_post",
            "post_id": post_id,
            "timestamp": datetime.now().isoformat(),
        }

        return self._post(f"{n8n_base_url}/webhook/generate-post", payload)

    # ── Get Scheduled Posts Tool ──────────────────────────────────────────────
    def get_scheduled_posts(
        self,
        n8n_base_url: str = "https://saitejagoud.app.n8n.cloud",
    ) -> list:

        payload = {
            "message": "Get all scheduled posts.",
            "action": "get_schedule",
            "timestamp": datetime.now().isoformat(),
        }

        result = self._post(
            f"{n8n_base_url}/webhook/schedule-post",
            payload
        )

        if result and "posts" in result:
            return result["posts"]

        return []

    # ── Internal helper ───────────────────────────────────────────────────────
    def _post(self, url: str, payload: dict) -> dict | None:
        """
        Send a POST request to an n8n webhook.
        Returns the response JSON with execution tracking.
        """

        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            execution_log = {
                "workflow_url": url,
                "status_code": response.status_code,
                "executed_at": datetime.now().isoformat(),
                "success": response.status_code == 200,
            }

            response.raise_for_status()

            if not response.content:
                return {
                    "success": True,
                    "execution_log": execution_log,
                }

            try:
                data = response.json()

                data["execution_log"] = execution_log

                return data

            except Exception:
                return {
                    "content": response.text,
                    "status": "generated",
                    "execution_log": execution_log,
                }

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "n8n not reachable",
                "execution_log": {
                    "workflow_url": url,
                    "executed_at": datetime.now().isoformat(),
                    "status": "connection_failed",
                },
            }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "n8n timeout",
                "execution_log": {
                    "workflow_url": url,
                    "executed_at": datetime.now().isoformat(),
                    "status": "timeout",
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_log": {
                    "workflow_url": url,
                    "executed_at": datetime.now().isoformat(),
                    "status": "failed",
                },
            }