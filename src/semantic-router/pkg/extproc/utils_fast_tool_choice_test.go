package extproc

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestExtractContentFast_ToolChoiceFacts(t *testing.T) {
	tests := []struct {
		name         string
		extra        string
		wantRequired bool
		wantNone     bool
	}{
		{name: "required", extra: `,"tool_choice":"required"`, wantRequired: true},
		{name: "named", extra: `,"tool_choice":{"type":"function","function":{"name":"lookup"}}`, wantRequired: true},
		{name: "none", extra: `,"tool_choice":"none"`, wantNone: true},
		{name: "legacy named", extra: `,"function_call":{"name":"lookup"}`, wantRequired: true},
		{name: "legacy none", extra: `,"function_call":"none"`, wantNone: true},
		{name: "auto", extra: `,"tool_choice":"auto"`},
		{name: "modern precedence", extra: `,"tool_choice":"none","function_call":{"name":"lookup"}`, wantNone: true},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			body := []byte(`{"model":"auto","messages":[{"role":"user","content":"hello"}]` + test.extra + `}`)
			got, err := extractContentFast(body)
			require.NoError(t, err)
			assert.Equal(t, test.wantRequired, got.ToolChoiceRequired)
			assert.Equal(t, test.wantNone, got.ToolChoiceNone)
		})
	}
}

func TestExtractContentFastAnthropic_ToolChoiceFacts(t *testing.T) {
	tests := []struct {
		name         string
		toolChoice   string
		wantRequired bool
		wantNone     bool
	}{
		{name: "any", toolChoice: `{"type":"any"}`, wantRequired: true},
		{name: "named", toolChoice: `{"type":"tool","name":"lookup"}`, wantRequired: true},
		{name: "none", toolChoice: `{"type":"none"}`, wantNone: true},
		{name: "auto", toolChoice: `{"type":"auto"}`},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			body := []byte(`{"model":"auto","tool_choice":` + test.toolChoice + `,"messages":[{"role":"user","content":"hello"}]}`)
			got, err := extractContentFastAnthropic(body)
			require.NoError(t, err)
			assert.Equal(t, test.wantRequired, got.ToolChoiceRequired)
			assert.Equal(t, test.wantNone, got.ToolChoiceNone)
		})
	}
}
