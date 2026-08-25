import requests
import json
import os
import base64
from datetime import datetime


class SocialMediaTools:
    """
    All tool functions the AI agent can call.

    n8n handles the main social-media workflows and OpenAI is used
    for LLM/image generation.
    """

    # ── Content Generation Tool ───────────────────────────────────────────────
    def generate_post(
        self,
        topic: str,
        platform: str,
        tone: str = "professional",
        include_hashtags: bool = True,
        n8n_base_url: str = "https://shankergoud.app.n8n.cloud",
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

        return self._post(
            f"{n8n_base_url}/webhook/generate-post",
            payload
        )

    # ── Image Generation Tool ───────────────────────────────────────────────
    def generate_image(
        self,
        topic: str,
        caption: str,
        platform: str,
        n8n_base_url: str = "https://shankergoud.app.n8n.cloud",
    ) -> dict:
        """
        Generate a social-media image using OpenAI Image Generation.

        The OpenAI API key is read from:
            OPENAI_API_KEY

        This replaces the previous Hugging Face / Qwen image generation.
        """

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return {
                "success": False,
                "error": "OPENAI_API_KEY is not configured."
            }

        image_prompt = (
            f"Create a professional social media image for {platform}. "
            f"Topic: {topic}. "
            f"Caption context: {caption}. "
            f"Create a visually attractive, realistic, high-quality "
            f"marketing image that visually represents the topic. "
            f"Create a standalone image, not a social media screenshot. "
            f"Do not create LinkedIn, Instagram, Facebook, Twitter, or "
            f"other social media interfaces. "
            f"Do not include logos, URLs, hashtags, captions, watermarks, "
            f"buttons, profile cards, phone screens, computer screens, "
            f"or unnecessary written text. "
            f"Use a clean composition suitable for {platform}."
        )

        try:

            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json={
                    "model": "gpt-image-1-mini",
                    "prompt": image_prompt,
                    "size": "1024x1024",
                    "quality": "auto",
                    "output_format": "png",
                },
                timeout=120,
            )

            response.raise_for_status()

            data = response.json()

            if not data.get("data"):
                return {
                    "success": False,
                    "error": "OpenAI Image API returned no image data."
                }

            image_data = data["data"][0].get("b64_json")

            if not image_data:
                return {
                    "success": False,
                    "error": "OpenAI Image API did not return base64 image data."
                }

            return {
                "success": True,
                "image_data": f"data:image/png;base64,{image_data}",
                "image_prompt": image_prompt,
                "model": "gpt-image-1-mini",
            }

        except requests.exceptions.Timeout:

            return {
                "success": False,
                "error": "OpenAI image generation timed out."
            }

        except requests.exceptions.RequestException as e:

            return {
                "success": False,
                "error": f"OpenAI image generation failed: {str(e)}"
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e)
            }

    # ── Schedule Post Tool ────────────────────────────────────────────────────
    def trigger_n8n_schedule(
        self,
        content: str,
        platform: str,
        schedule_time: str,
        image_data: str = "",
        n8n_base_url: str = "https://shankergoud.app.n8n.cloud",
    ) -> dict:

        payload = {
            "message": (
                f"Schedule this {platform} post for "
                f"{schedule_time}: {content}"
            ),
            "action": "schedule_post",
            "content": content,
            "platform": platform.lower(),
            "schedule_time": schedule_time,
            "image_data": image_data,
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
        n8n_base_url: str = "https://shankergoud.app.n8n.cloud",
    ) -> dict:

        payload = {
            "message": (
                f"Fetch and analyze analytics for "
                f"{platform} over {date_range}."
            ),
            "action": "fetch_analytics",
            "platform": platform.lower(),
            "date_range": date_range,
            "timestamp": datetime.now().isoformat(),
        }

        return self._post(
            f"{n8n_base_url}/webhook/get-analytics",
            payload
        )

    # ── Approve & Publish Tool ────────────────────────────────────────────────
    def approve_and_publish(
        self,
        post_id: str,
        n8n_base_url: str = "https://shankergoud.app.n8n.cloud",
    ) -> dict:

        payload = {
            "message": f"Approve and publish post with ID: {post_id}",
            "action": "approve_post",
            "post_id": post_id,
            "timestamp": datetime.now().isoformat(),
        }

        return self._post(
            f"{n8n_base_url}/webhook/generate-post",
            payload
        )

    # ── Get Scheduled Posts Tool ──────────────────────────────────────────────
    def get_scheduled_posts(
        self,
        n8n_base_url: str = "https://shankergoud.app.n8n.cloud",
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
                headers={
                    "Content-Type": "application/json"
                },
                timeout=180,
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