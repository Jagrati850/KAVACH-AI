"""
KAVACH AI — Multi-Agent AI Orchestrator
Central coordinator for all AI analysis agents.
Routes requests to specialized engines and aggregates results.
"""

import asyncio
from typing import Any, Dict, Optional

from app.ai.scam_detector.engine import ScamDetectorEngine
from app.ai.currency_detector.engine import CurrencyDetectorEngine
from app.ai.deepfake_detector.engine import DeepfakeDetectorEngine
from app.ai.call_scam_classifier import CallScamClassifier


class AIOrchestrator:
    """
    Multi-Agent Orchestrator that coordinates specialized AI engines.

    Architecture:
    ┌─────────────────────────────────────────┐
    │            AI ORCHESTRATOR              │
    │         (Request Router)               │
    └─────┬──────┬──────┬──────┬──────┬──────┘
          │      │      │      │      │
    ┌─────▼┐ ┌───▼──┐ ┌─▼───┐ ┌▼────┐ ┌▼───┐
    │Scam  │ │Curr. │ │Deep │ │Fraud│ │Geo │
    │Agent │ │Agent │ │fake │ │Graph│ │    │
    └──────┘ └──────┘ └─────┘ └─────┘ └────┘
    """

    def __init__(self):
        self.scam_engine = ScamDetectorEngine()
        self.currency_engine = CurrencyDetectorEngine()
        self.deepfake_engine = DeepfakeDetectorEngine()
        self.call_scam_classifier = CallScamClassifier()

    async def analyze_call_transcript(
        self,
        transcript: str,
        language: str = "auto",
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route call transcripts to the trained ML Call Scam Classifier
        (15-category TF-IDF + LogisticRegression model). Used by the
        Call Transcripts scan endpoints only.
        """
        return await self.call_scam_classifier.analyze(
            transcript=transcript,
            language=language,
            context=context,
        )

    async def analyze_scam_text(
        self,
        text: str,
        language: str = "auto",
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route text analysis to the Scam Detection Engine.
        Returns structured analysis with confidence score and verdict.
        """
        return await self.scam_engine.analyze(
            text=text,
            language=language,
            context=context,
        )

    async def analyze_currency(
        self,
        image_data: bytes,
        denomination: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route currency image to the Currency Detection Engine.
        Returns authenticity analysis with feature-level scores.
        """
        return await self.currency_engine.analyze(
            image_data=image_data,
            denomination=denomination,
        )

    async def analyze_deepfake_image(
        self,
        image_data: bytes,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route image to the Deepfake Detection Engine.
        Returns manipulation analysis with artifact detection scores.
        """
        return await self.deepfake_engine.analyze_image(
            image_data=image_data,
            context=context,
        )

    async def analyze_deepfake_audio(
        self,
        audio_data: bytes,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route audio data to the Deepfake Detection Engine.
        Returns voice clone analysis.
        """
        return await self.deepfake_engine.analyze_audio(
            audio_data=audio_data,
            context=context,
        )


    async def run_comprehensive_analysis(
        self,
        text: Optional[str] = None,
        image_data: Optional[bytes] = None,
        context: str = "general",
    ) -> Dict[str, Any]:
        """
        Run multiple AI agents in parallel and aggregate results.
        Used for comprehensive threat assessment.
        """
        tasks = []
        agent_names = []

        if text:
            tasks.append(self.analyze_scam_text(text=text, context=context))
            agent_names.append("scam_detector")

        if image_data:
            tasks.append(self.analyze_currency(image_data=image_data))
            agent_names.append("currency_detector")
            tasks.append(self.analyze_deepfake_image(image_data=image_data, context=context))
            agent_names.append("deepfake_detector")

        if not tasks:
            return {"error": "No input provided for analysis"}

        # Run all agents in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        agent_results = {}
        overall_risk = 0.0
        successful_agents = 0

        for name, result in zip(agent_names, results):
            if isinstance(result, Exception):
                agent_results[name] = {
                    "status": "error",
                    "error": str(result),
                }
            else:
                agent_results[name] = {
                    "status": "success",
                    "result": result,
                }
                overall_risk += result.get("confidence_score", 0)
                successful_agents += 1

        if successful_agents > 0:
            overall_risk /= successful_agents

        # Determine overall verdict
        if overall_risk >= 0.7:
            overall_verdict = "dangerous"
        elif overall_risk >= 0.4:
            overall_verdict = "suspicious"
        else:
            overall_verdict = "safe"

        return {
            "overall_risk_score": round(overall_risk, 4),
            "overall_verdict": overall_verdict,
            "agents_run": len(tasks),
            "agents_succeeded": successful_agents,
            "agent_results": agent_results,
        }
