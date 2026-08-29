package extproc

import (
	"encoding/json"

	"github.com/tidwall/gjson"

	"github.com/vllm-project/semantic-router/src/semantic-router/pkg/classification"
)

func populateFastOpenAIToolChoiceFacts(body []byte, result *FastExtractResult) {
	facts := classification.ResolveOpenAIToolChoiceFacts(
		rawMessageFromGJSON(gjson.GetBytes(body, "tool_choice")),
		rawMessageFromGJSON(gjson.GetBytes(body, "function_call")),
	)
	result.ToolChoiceRequired = facts.Required
	result.ToolChoiceNone = facts.None
}

func populateFastAnthropicToolChoiceFacts(body []byte, result *FastExtractResult) {
	facts := classification.ResolveAnthropicToolChoiceFacts(
		rawMessageFromGJSON(gjson.GetBytes(body, "tool_choice")),
	)
	result.ToolChoiceRequired = facts.Required
	result.ToolChoiceNone = facts.None
}

func rawMessageFromGJSON(value gjson.Result) json.RawMessage {
	if !value.Exists() {
		return nil
	}
	return json.RawMessage(value.Raw)
}
