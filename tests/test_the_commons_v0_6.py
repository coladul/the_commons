from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from agents import Agent
from agents.items import MessageOutputItem
from openai.types.responses import ResponseOutputMessage

import the_commons_v0_6 as v06


class SerializationRegressionTests(unittest.TestCase):
    @staticmethod
    def sdk_item(output_type: type) -> MessageOutputItem:
        agent = Agent(name="serialization regression probe", output_type=output_type)
        raw_item = ResponseOutputMessage(
            id="msg_regression_probe",
            content=[],
            role="assistant",
            status="completed",
            type="message",
        )
        return MessageOutputItem(agent=agent, raw_item=raw_item)

    def test_exact_failed_pilot_class_serialization_failure_is_fixed(self) -> None:
        failed_path = v06.FAILED_EXECUTED_SCRIPT_PATH
        spec = importlib.util.spec_from_file_location("failed_v06_regression", failed_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        failed_v06 = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = failed_v06
        try:
            spec.loader.exec_module(failed_v06)
            failed_item = self.sdk_item(failed_v06.ChildRevision)
            with self.assertRaisesRegex(
                TypeError,
                r"BaseModel\.model_dump\(\) missing 1 required positional argument: 'self'",
            ):
                failed_v06.to_jsonable([failed_item])
        finally:
            sys.modules.pop(spec.name, None)

        fixed_item = self.sdk_item(v06.ChildRevision)
        serialized = v06.to_jsonable([fixed_item])
        output_type = serialized[0]["agent"]["output_type"]
        self.assertEqual(output_type["__kind__"], "python_class")
        self.assertEqual(output_type["module"], "the_commons_v0_6")
        self.assertEqual(output_type["qualname"], "ChildRevision")
        json.dumps(serialized)

    def test_essential_record_is_committed_before_optional_sdk_internals(self) -> None:
        world = v06.make_worlds()[0]
        trial = v06.build_trials([world])[0]
        revision = v06.ChildRevision(
            temperature_relation="<=",
            temperature_cutoff=world.max_hunt_temp,
            density_relation=">=",
            density_cutoff=world.min_hunt_density,
            logic="AND",
            archive_assessment="not_applicable",
            confidence=0.9,
            commons_claim="Preserve the scored rule.",
            evidence_summary="The confirmed observations identify both boundaries.",
            rationale="This rule matches the entire objective scoring domain.",
        )
        usage = SimpleNamespace(
            requests=1,
            input_tokens=101,
            output_tokens=37,
            total_tokens=138,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "trial.json"

            class ExplodingSDKInternal:
                observed_committed_record: dict | None = None

                def model_dump(self, mode: str = "json") -> dict:
                    del mode
                    self.observed_committed_record = json.loads(
                        output_path.read_text(encoding="utf-8")
                    )
                    raise RuntimeError("optional SDK serialization probe")

            exploding = ExplodingSDKInternal()
            result = SimpleNamespace(
                last_response_id="resp_regression_probe",
                raw_responses=[],
                new_items=exploding,
                last_agent=v06.ChildRevision,
            )
            raw_record = {
                "experiment": v06.EXPERIMENT_NAME,
                "phase": v06.PHASE,
                "trial_id": trial.trial_id,
                "world": world.to_dict(),
                "condition": trial.condition,
            }

            correct, possible, optional_errors = v06.commit_successful_trial_record(
                output_path,
                raw_record,
                trial,
                revision,
                usage,
                result,
            )
            saved = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertIsNotNone(exploding.observed_committed_record)
        first_commit = exploding.observed_committed_record
        self.assertEqual(first_commit["status"], "parsed")
        self.assertTrue(first_commit["essential_record_committed"])
        self.assertNotIn("new_items", first_commit)
        self.assertEqual(first_commit["response_id"], "resp_regression_probe")
        self.assertEqual(first_commit["formal_rule"], v06.formal_rule(revision))
        self.assertEqual(first_commit["rationale"], revision.rationale)
        self.assertEqual(first_commit["usage"]["total_tokens"], 138)

        self.assertEqual(correct, possible)
        self.assertEqual(possible, 4141)
        self.assertTrue(saved["semantic_equivalent"])
        self.assertEqual(saved["status"], "parsed")
        self.assertEqual(len(optional_errors), 1)
        self.assertEqual(optional_errors[0]["field"], "new_items")
        self.assertTrue(saved["new_items"]["__serialization_failed__"])
        self.assertFalse(saved["optional_serialization_complete"])

    def test_failed_and_replacement_pilot_namespaces_are_distinct(self) -> None:
        self.assertNotEqual(v06.FAILED_PILOT_ROOT.resolve(), v06.ARTIFACT_ROOT.resolve())
        self.assertEqual(v06.ARTIFACT_ROOT.name, "replacement_pilot_01")
        self.assertTrue(v06.validate_failed_pilot_immutable()["pass"])


if __name__ == "__main__":
    unittest.main()

