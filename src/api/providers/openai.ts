import { Anthropic } from "@anthropic-ai/sdk"
import OpenAI, { AzureOpenAI } from "openai"
import { withRetry } from "../retry"
import { ApiHandlerOptions, azureOpenAiDefaultApiVersion, ModelInfo, openAiModelInfoSaneDefaults } from "../../shared/api"
import { ApiHandler } from "../index"
import { convertToOpenAiMessages } from "../transform/openai-format"
import { ApiStream } from "../transform/stream"
import { convertToR1Format } from "../transform/r1-format"
import { ChatCompletionReasoningEffort } from "openai/resources/chat/completions.mjs"

export class OpenAiHandler implements ApiHandler {
	private options: ApiHandlerOptions
	private client: OpenAI

	constructor(options: ApiHandlerOptions) {
		this.options = options
		// Azure API shape slightly differs from the core API shape: https://github.com/openai/openai-node?tab=readme-ov-file#microsoft-azure-openai
		// Use azureApiVersion to determine if this is an Azure endpoint, since the URL may not always contain 'azure.com'
		if (this.options.azureApiVersion || this.options.openAiBaseUrl?.toLowerCase().includes("azure.com")) {
			this.client = new AzureOpenAI({
				baseURL: this.options.openAiBaseUrl,
				apiKey: this.options.openAiApiKey,
				apiVersion: this.options.azureApiVersion || azureOpenAiDefaultApiVersion,
			})
		} else {
			this.client = new OpenAI({
				baseURL: this.options.openAiBaseUrl,
				apiKey: this.options.openAiApiKey,
			})
		}
	}

	@withRetry()
	async *createMessage(systemPrompt: string, messages: Anthropic.Messages.MessageParam[]): ApiStream {
		const modelId = this.options.openAiModelId ?? ""
		const isDeepseekReasoner = modelId.includes("deepseek-reasoner")
		const isO3Mini = modelId.includes("o3-mini")
		const supportsStreaming = this.options.openAiModelInfo?.supportsStreaming ?? true

		// Debugging: Log request details
		console.log("====== OpenAI API Request Details ======")
		console.log(`Base URL: ${this.client.baseURL}`)
		console.log(`Model ID: ${modelId}`)
		console.log("Custom Headers:", JSON.stringify(this.options.openAiCustomHeaders, null, 2))

		let openAiMessages: OpenAI.Chat.ChatCompletionMessageParam[] = [
			{ role: "system", content: systemPrompt },
			...convertToOpenAiMessages(messages),
		]
		let temperature: number | undefined = this.options.openAiModelInfo?.temperature ?? openAiModelInfoSaneDefaults.temperature
		let reasoningEffort: ChatCompletionReasoningEffort | undefined = undefined

		// Enhanced debugging logs with more detailed information
		console.log("====== OpenAI API Configuration Details ======")
		console.log(`Base URL: ${this.client.baseURL}`)
		console.log(`Model ID: ${modelId}`)
		console.log(`API Key Present: ${!!this.options.openAiApiKey}`)
		console.log(`Raw supportsStreaming value: ${JSON.stringify(this.options.openAiModelInfo?.supportsStreaming)}`)
		console.log(`Temperature: ${temperature}`)
		console.log(
			`Using Model-Specific Format: ${isDeepseekReasoner ? "DeepSeek Reasoner" : isO3Mini ? "O3-Mini" : "Standard"}`,
		)
		console.log("Custom Headers:", JSON.stringify(this.options.openAiCustomHeaders, null, 2))
		console.log(`Raw Message Count: ${messages.length}`)

		if (isDeepseekReasoner) {
			openAiMessages = convertToR1Format([{ role: "user", content: systemPrompt }, ...messages])
		}

		if (isO3Mini) {
			openAiMessages = [{ role: "developer", content: systemPrompt }, ...convertToOpenAiMessages(messages)]
			temperature = undefined // does not support temperature
			reasoningEffort = (this.options.o3MiniReasoningEffort as ChatCompletionReasoningEffort) || "medium"
		}

		// Parse the JSON string custom headers into an object if they exist
		const customHeaders = this.options.openAiCustomHeaders ? JSON.parse(this.options.openAiCustomHeaders) : undefined

		// Create request parameters
		const requestParams: any = {
			model: modelId,
			messages: openAiMessages,
			temperature,
		}

		if (reasoningEffort !== undefined) {
			requestParams.reasoning_effort = reasoningEffort
		}

		// Handle streaming vs non-streaming API calls
		if (supportsStreaming) {
			// Set streaming specific parameters
			const streamParams = {
				...requestParams,
				stream: true,
				stream_options: { include_usage: true },
			}

			const stream = await this.client.chat.completions.create(streamParams, {
				headers: customHeaders,
			})

			// Explicitly cast stream to a type that supports async iteration
			const streamIterable = stream as unknown as AsyncIterable<OpenAI.Chat.Completions.ChatCompletionChunk>

			for await (const chunk of streamIterable) {
				const delta = chunk.choices[0]?.delta
				if (delta?.content) {
					yield {
						type: "text",
						text: delta.content,
					}
				}

				if (delta && "reasoning_content" in delta && delta.reasoning_content) {
					yield {
						type: "reasoning",
						reasoning: (delta.reasoning_content as string | undefined) || "",
					}
				}

				if (chunk.usage) {
					yield {
						type: "usage",
						inputTokens: chunk.usage.prompt_tokens || 0,
						outputTokens: chunk.usage.completion_tokens || 0,
					}
				}
			}
		} else {
			// For non-streaming, explicitly set stream to false
			const nonStreamParams = {
				...requestParams,
				stream: false,
			}

			try {
				// Log the request payload
				console.log("====== OpenAI API Request Payload ======")
				console.log(JSON.stringify(nonStreamParams, null, 2))

				// Make a non-streaming API call
				const response = await this.client.chat.completions.create(nonStreamParams, {
					headers: customHeaders,
				})

				// Simulate streaming by yielding the entire content at once
				if (response.choices && response.choices.length > 0) {
					const choice = response.choices[0]
					if (choice.message && choice.message.content) {
						yield {
							type: "text",
							text: choice.message.content,
						}
					}
				}

				// Yield usage information if available
				if (response.usage) {
					yield {
						type: "usage",
						inputTokens: response.usage.prompt_tokens || 0,
						outputTokens: response.usage.completion_tokens || 0,
					}
				}
			} catch (error) {
				console.error("Error in non-streaming OpenAI API call:", error)

				// Enhanced error logging
				console.error("====== OpenAI API Error Details ======")
				// Log more details about the error
				if (error && typeof error === "object") {
					// Log the error status
					console.error(`Status code: ${(error as any).status || "unknown"}`)

					// Log the error message
					console.error(`Error message: ${(error as any).message || "No message available"}`)

					// Log any response body
					if ((error as any).response) {
						console.error(
							"Response body:",
							(error as any).response.data || (error as any).response.body || "No response body available",
						)
					}

					// Log request ID if available
					if ((error as any).request_id) {
						console.error(`Request ID: ${(error as any).request_id}`)
					}

					// Log the error detail/code
					if ((error as any).error) {
						console.error("Error details:", (error as any).error)
					}

					// Log headers if available
					if ((error as any).headers) {
						console.error("Response headers:", (error as any).headers)
					}
				}

				throw error
			}
		}
	}

	getModel(): { id: string; info: ModelInfo } {
		return {
			id: this.options.openAiModelId ?? "",
			info: this.options.openAiModelInfo ?? openAiModelInfoSaneDefaults,
		}
	}
}
