import Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { z } from "zod";

const MODEL = "claude-sonnet-5";

const BlogPostSchema = z.object({
  topic: z
    .string()
    .describe("이번 글의 주제를 짧게 요약한 키워드 (예: '스케일링 주기'). 다음 실행에서 중복 방지용 이력으로 저장된다."),
  title: z.string().describe("블로그 글 제목"),
  contentHtml: z
    .string()
    .describe(
      "Blogger 글 본문. <h2>, <p>, <ul>/<li> 등 기본 HTML 태그만 사용. 800~1200자 분량의 정보성 글."
    ),
  labels: z
    .array(z.string())
    .min(1)
    .max(5)
    .describe("Blogger 라벨(태그) 목록"),
});

export type GeneratedBlogPost = z.infer<typeof BlogPostSchema>;

const GUARDRAILS = `
다음을 반드시 지켜라 (의료법상 의료광고 규제 위반 소지를 피하기 위함):
- 특정 치료의 효과를 보장하거나 단정하는 표현 금지 ("100% 낫는다", "완치 보장" 등)
- 시술 전후 비교(before/after) 서술 금지
- 환자 후기나 만족도 인용 금지 (가상의 후기 포함)
- 특정 시술의 할인, 이벤트, 가격을 홍보하는 소구 금지
- "최고", "1위", "유일" 등 과장 표현 금지
- 진단이나 처방을 대신하는 듯한 확정적 조언 금지 ("반드시 임플란트를 해야 한다" 등) — 항상
  "정확한 진단은 치과 방문 후 상담하세요" 같은 일반적 안내로 마무리
- 톤은 친절하고 이해하기 쉬운 정보 제공형 블로그. 특정 병원 홍보보다는 독자에게 도움이 되는
  치아/구강 건강 지식 전달이 목적.
`.trim();

const TOPIC_CATEGORIES = [
  "치아 관리 습관 (양치, 치실, 구강청결제 등)",
  "스케일링/치석 관리",
  "충치 예방 및 초기 증상",
  "임플란트 일반 정보 (원리, 관리법, 수명 등 — 특정 시술 홍보 아님)",
  "소아 치과 (유치 관리, 아이 첫 치과 방문 등)",
  "사랑니 관련 일반 정보",
  "잇몸 건강 (치주염, 잇몸 출혈 등)",
  "치아 착색/미백 일반 정보",
  "교정 치료 일반 정보",
  "구강 건강과 전신 건강의 관계",
];

function buildSystemPrompt(recentTopics: string[]): string {
  const avoidList =
    recentTopics.length > 0
      ? `최근에 이미 다룬 주제 (겹치지 않게 다른 주제를 골라라):\n${recentTopics
          .map((t) => `- ${t}`)
          .join("\n")}`
      : "아직 작성된 글이 없다. 자유롭게 주제를 골라라.";

  return `너는 대한민국 원주에 있는 "원주 건강한치과"의 블로그 작성을 돕는 콘텐츠 작가다.
이 블로그(healthydentalwonju.blogspot.com)는 일반 치과 상식을 전달하는 정보성 블로그다.

아래 카테고리 중 하나를 골라 새 글을 한 편 작성하라:
${TOPIC_CATEGORIES.map((c) => `- ${c}`).join("\n")}

${avoidList}

${GUARDRAILS}

출력은 지정된 JSON 스키마 형식을 그대로 따르라.`;
}

let client: Anthropic | null = null;
function getClient(): Anthropic {
  if (!client) client = new Anthropic();
  return client;
}

export async function generateBlogPost(
  recentTopics: string[]
): Promise<GeneratedBlogPost> {
  const response = await getClient().messages.parse({
    model: MODEL,
    max_tokens: 4000,
    system: buildSystemPrompt(recentTopics),
    messages: [
      {
        role: "user",
        content: "오늘 올릴 블로그 글 한 편을 작성해줘.",
      },
    ],
    output_config: {
      format: zodOutputFormat(BlogPostSchema),
    },
  });

  if (!response.parsed_output) {
    throw new Error("Claude 응답을 스키마에 맞게 파싱하지 못했습니다.");
  }
  return response.parsed_output;
}
