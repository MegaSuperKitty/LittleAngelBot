(() => {
  const LANG_KEY = "angel_console_lang";

  const I18N = {
    zh: {
      brand_kicker: "LittleAngel",
      brand_title: "Agent控制台",
      brand_desc: "",
      nav_chat: "聊天",
      nav_search: "搜索任务",
      nav_channels: "频道",
      nav_cron: "定时任务",
      nav_heartbeat: "心跳",
      nav_skills: "技能",
      nav_models: "模型",
      nav_billing: "模型计费",
      channels_title: "频道",
      channels_subtitle: "管理浏览器、CLI、QQ 与 Discord 连接渠道",
      channel_enabled_label: "启用",
      channel_prefix_label: "Bot 前缀",
      channel_prefix_placeholder: "可选前缀（例如 @bot）",
      sessions_title: "会话",
      new_web_session: "新建 Web 会话",
      filter_all: "全部",
      filter_qq: "QQ",
      filter_cli: "CLI",
      filter_web: "WEB",
      chat_subtitle_default: "请选择一个会话继续。",
      btn_cancel: "取消任务",
      btn_refresh: "刷新",
      btn_upload: "上传文件",
      btn_voice_start: "开始语音",
      btn_voice_stop: "停止录音",
      btn_send: "发送",
      voice_idle: "待机",
      voice_recording: "录音中...",
      voice_transcribing: "转写中...",
      voice_unsupported: "浏览器不支持录音",
      voice_permission_denied: "麦克风权限被拒绝",
      voice_empty: "未采集到语音",
      voice_transcribed: "已转写",
      trace_title: "ReAct 追踪",
      input_message_placeholder: "输入消息，Ctrl/Cmd + Enter 发送...",
      search_title: "搜索任务",
      search_subtitle: "在历史会话中检索，并跳转到最相关上下文。",
      search_placeholder: "输入关键词或问题",
      search_limit_placeholder: "条数",
      search_status_ready: "索引就绪",
      search_status_indexing: "索引中",
      search_status_last_index: "上次索引",
      search_status_chunks: "分片数",
      search_status_files: "文件数",
      search_status_embedder: "嵌入模型",
      search_no_results: "没有命中结果。",
      search_open_session: "打开会话",
      search_score: "相关度",
      btn_search: "搜索",
      btn_reindex: "重建索引",
      filter_all_channels: "全部频道",
      cron_title: "Cron 任务",
      btn_reload: "刷新",
      cron_create_title: "新建任务",
      cron_expr_placeholder: "cron 表达式，例如 */5 * * * *",
      user_id_placeholder: "用户 ID",
      session_optional_placeholder: "会话名（可选）",
      prompt_placeholder: "提示词",
      btn_create: "创建",
      heartbeat_title: "心跳",
      hb_enabled: "启用",
      hb_interval_placeholder: "间隔秒数",
      hb_prompt_placeholder: "心跳提示词",
      btn_save: "保存",
      btn_run_once: "立即执行",
      skills_title: "技能",
      skills_subtitle: "从本地工作目录 skills 读取。",
      models_title: "模型配置",
      models_subtitle: "管理 provider、密钥、profile，并切换当前工作模型。",
      providers_title: "提供商",
      profile_editor_title: "Profile 编辑器",
      profiles_title: "Profiles",
      runtime_title: "当前运行配置",
      field_profile_id: "Profile ID",
      field_provider: "提供商",
      field_base_url: "Base URL",
      field_model_name: "模型名",
      field_api_key: "API Key",
      field_max_tokens: "Max Tokens",
      field_timeout: "超时（秒）",
      field_temperature: "Temperature",
      field_top_p: "Top-p（核采样）",
      profile_id_placeholder: "profile_id",
      base_url_placeholder: "base_url",
      model_name_placeholder: "model",
      api_key_placeholder: "api_key（必填）",
      max_tokens_placeholder: "max_tokens（可选）",
      timeout_placeholder: "timeout 秒（可选）",
      temperature_placeholder: "temperature（可选）",
      top_p_placeholder: "top_p（可选）",
      clear_api_key: "清空已有 API Key",
      btn_new: "新建",
      btn_save_profile: "保存 Profile",
      btn_activate: "设为工作模型",
      btn_delete: "删除",
      service_checking: "服务：检查中...",
      service_online: "服务：在线",
      service_offline: "服务：离线",
      no_channels: "暂无频道配置。",
      no_sessions: "暂无会话。",
      no_cron_jobs: "暂无 cron 任务。",
      no_skills: "未检测到 skills。",
      no_profiles: "暂无 profile。",
      waiting_input: "等待你的输入...",
      human_input_submitted: "已提交",
      action_failed: "操作失败",
      upload_failed: "上传失败",
      init_failed: "初始化失败",
      stream_failed: "流式请求失败",
      btn_pause: "暂停",
      btn_resume: "恢复",
      btn_run: "执行",
      cron_expr_label: "表达式",
      target_label: "目标",
      status_label: "状态",
      paused_label: "暂停",
      next_run_label: "下次执行",
      last_run_label: "上次执行",
      last_result_label: "结果",
      hb_state_last_run: "上次执行",
      hb_state_last_status: "上次状态",
      hb_state_last_result: "上次结果",
      lang_toggle_button: "EN",
      lang_toggle_title: "Switch to English",
      payload_tool: "工具",
      payload_args: "参数",
      payload_state: "状态",
      payload_phase: "阶段",
      payload_error: "错误",
      event_connected: "已连接",
      event_run_started: "任务开始",
      event_assistant_reason: "调用理由",
      event_tool_before: "工具调用前",
      event_tool_after: "工具调用后",
      event_ask_human: "等待人工输入",
      event_status: "状态",
      event_assistant_delta: "回复流",
      event_run_done: "任务结束",
      event_cancel: "取消",
      event_human_input: "人工输入",
      event_file_uploaded: "文件上传",
      skill_path: "路径",
      provider_authorized: "已授权",
      provider_unauthorized: "未授权",
      profile_active: "工作中",
      profile_inactive: "未激活",
      runtime_provider: "Provider",
      runtime_model: "Model",
      runtime_base_url: "Base URL",
      runtime_key: "API Key",
      runtime_valid: "可用性",
      runtime_valid_yes: "可用",
      runtime_valid_no: "不可用",
      runtime_error: "错误",
      runtime_empty: "暂无运行配置。",
      select_profile_placeholder: "选择已有 profile",
      billing_title: "模型计费",
      billing_subtitle: "查看调用量、Token 消耗、失败率和单次调用详情。",
      billing_range_12h: "最近 12 小时",
      billing_range_24h: "最近 24 小时",
      billing_range_7d: "最近 7 天",
      billing_range_30d: "最近 30 天",
      billing_range_custom: "自定义",
      billing_bucket_auto: "自动粒度",
      billing_provider_placeholder: "provider",
      billing_model_placeholder: "model",
      billing_profile_placeholder: "profile_id",
      billing_keyword_placeholder: "关键词",
      billing_status_all: "全部",
      billing_status_success: "成功",
      billing_status_failed: "失败",
      billing_apply_filters: "应用筛选",
      billing_calls_total: "总调用",
      billing_success_calls: "成功",
      billing_failed_calls: "失败",
      billing_failure_rate: "失败率",
      billing_prompt_tokens: "输入 Token",
      billing_completion_tokens: "输出 Token",
      billing_tokens_total: "总 Token",
      billing_latency_p95: "P95 耗时",
      billing_chart_calls: "调用次数趋势",
      billing_chart_tokens: "Token 趋势",
      billing_call_list: "调用明细",
      billing_prev_page: "上一页",
      billing_next_page: "下一页",
      billing_detail_title: "调用详情",
      billing_no_data: "暂无数据",
      billing_status_box: "日志目录",
    },
    en: {
      brand_kicker: "LittleAngel",
      brand_title: "Agent Console",
      brand_desc: "",
      nav_chat: "Chat",
      nav_search: "Search Tasks",
      nav_channels: "Channels",
      nav_cron: "Cron",
      nav_heartbeat: "Heartbeat",
      nav_skills: "Skills",
      nav_models: "Models",
      nav_billing: "Billing",
      channels_title: "Channels",
      channels_subtitle: "Manage browser, cli, qq and discord channel connections.",
      channel_enabled_label: "Enabled",
      channel_prefix_label: "Bot Prefix",
      channel_prefix_placeholder: "optional prefix, e.g. @bot",
      sessions_title: "Sessions",
      new_web_session: "New Web Session",
      filter_all: "All",
      filter_qq: "QQ",
      filter_cli: "CLI",
      filter_web: "WEB",
      chat_subtitle_default: "Select a session to continue.",
      btn_cancel: "Cancel",
      btn_refresh: "Refresh",
      btn_upload: "Upload",
      btn_voice_start: "Start Voice",
      btn_voice_stop: "Stop Recording",
      btn_send: "Send",
      voice_idle: "Idle",
      voice_recording: "Recording...",
      voice_transcribing: "Transcribing...",
      voice_unsupported: "Browser does not support recording",
      voice_permission_denied: "Microphone permission denied",
      voice_empty: "No audio captured",
      voice_transcribed: "Transcribed",
      trace_title: "ReAct Trace",
      input_message_placeholder: "Type your message, Ctrl/Cmd + Enter to send...",
      search_title: "Search Tasks",
      search_subtitle: "Search historical sessions and jump to the best match.",
      search_placeholder: "Type query or question",
      search_limit_placeholder: "limit",
      search_status_ready: "Index ready",
      search_status_indexing: "Indexing",
      search_status_last_index: "Last indexed",
      search_status_chunks: "Chunks",
      search_status_files: "Files",
      search_status_embedder: "Embedder",
      search_no_results: "No relevant results.",
      search_open_session: "Open session",
      search_score: "Score",
      btn_search: "Search",
      btn_reindex: "Reindex",
      filter_all_channels: "All Channels",
      cron_title: "Cron Jobs",
      btn_reload: "Reload",
      cron_create_title: "Create Job",
      cron_expr_placeholder: "cron expression, e.g. */5 * * * *",
      user_id_placeholder: "user_id",
      session_optional_placeholder: "session_name (optional)",
      prompt_placeholder: "Prompt",
      btn_create: "Create",
      heartbeat_title: "Heartbeat",
      hb_enabled: "Enabled",
      hb_interval_placeholder: "interval seconds",
      hb_prompt_placeholder: "Heartbeat prompt",
      btn_save: "Save",
      btn_run_once: "Run Once",
      skills_title: "Skills",
      skills_subtitle: "Loaded from local workspace skills directory.",
      models_title: "Model Config",
      models_subtitle: "Manage providers, keys, profiles and active runtime model.",
      providers_title: "Providers",
      profile_editor_title: "Profile Editor",
      profiles_title: "Profiles",
      runtime_title: "Runtime Config",
      field_profile_id: "Profile ID",
      field_provider: "Provider",
      field_base_url: "Base URL",
      field_model_name: "Model",
      field_api_key: "API Key",
      field_max_tokens: "Max Tokens",
      field_timeout: "Timeout (s)",
      field_temperature: "Temperature",
      field_top_p: "Top-p",
      profile_id_placeholder: "profile_id",
      base_url_placeholder: "base_url",
      model_name_placeholder: "model",
      api_key_placeholder: "api_key (required)",
      max_tokens_placeholder: "max_tokens (optional)",
      timeout_placeholder: "timeout seconds (optional)",
      temperature_placeholder: "temperature (optional)",
      top_p_placeholder: "top_p (optional)",
      clear_api_key: "Clear existing API key",
      btn_new: "New",
      btn_save_profile: "Save Profile",
      btn_activate: "Activate",
      btn_delete: "Delete",
      lang_toggle_button: "中文",
      lang_toggle_title: "切换到中文",
      service_checking: "Service: checking...",
      service_online: "Service: online",
      service_offline: "Service: offline",
      no_channels: "No channel config.",
      no_sessions: "No sessions.",
      no_cron_jobs: "No cron jobs.",
      no_skills: "No skills found.",
      no_profiles: "No profiles.",
      waiting_input: "Waiting for your input...",
      human_input_submitted: "submitted",
      action_failed: "Action failed",
      upload_failed: "Upload failed",
      init_failed: "Failed to initialize console",
      stream_failed: "stream_failed",
      btn_pause: "Pause",
      btn_resume: "Resume",
      btn_run: "Run",
      cron_expr_label: "expr",
      target_label: "target",
      status_label: "status",
      paused_label: "paused",
      next_run_label: "next_run_ts",
      last_run_label: "last_run_at",
      last_result_label: "last_result",
      hb_state_last_run: "last_run_at",
      hb_state_last_status: "last_status",
      hb_state_last_result: "last_result",
      payload_tool: "tool",
      payload_args: "args",
      payload_state: "state",
      payload_phase: "phase",
      payload_error: "error",
      event_connected: "connected",
      event_run_started: "run_started",
      event_assistant_reason: "assistant_reason",
      event_tool_before: "tool_before",
      event_tool_after: "tool_after",
      event_ask_human: "ask_human",
      event_status: "status",
      event_assistant_delta: "assistant_delta",
      event_run_done: "run_done",
      event_cancel: "cancel",
      event_human_input: "human_input",
      event_file_uploaded: "file_uploaded",
      skill_path: "path",
      provider_authorized: "authorized",
      provider_unauthorized: "unauthorized",
      profile_active: "active",
      profile_inactive: "inactive",
      runtime_provider: "Provider",
      runtime_model: "Model",
      runtime_base_url: "Base URL",
      runtime_key: "API Key",
      runtime_valid: "Valid",
      runtime_valid_yes: "yes",
      runtime_valid_no: "no",
      runtime_error: "Error",
      runtime_empty: "No runtime info.",
      select_profile_placeholder: "Select existing profile",
      billing_title: "Model Billing",
      billing_subtitle: "Inspect call volume, token usage, failures and per-call details.",
      billing_range_12h: "Last 12h",
      billing_range_24h: "Last 24h",
      billing_range_7d: "Last 7d",
      billing_range_30d: "Last 30d",
      billing_range_custom: "Custom",
      billing_bucket_auto: "Auto Bucket",
      billing_provider_placeholder: "provider",
      billing_model_placeholder: "model",
      billing_profile_placeholder: "profile_id",
      billing_keyword_placeholder: "keyword",
      billing_status_all: "all",
      billing_status_success: "success",
      billing_status_failed: "failed",
      billing_apply_filters: "Apply",
      billing_calls_total: "Total Calls",
      billing_success_calls: "Success",
      billing_failed_calls: "Failed",
      billing_failure_rate: "Failure Rate",
      billing_prompt_tokens: "Prompt Tokens",
      billing_completion_tokens: "Completion Tokens",
      billing_tokens_total: "Total Tokens",
      billing_latency_p95: "P95 Latency",
      billing_chart_calls: "Call Volume",
      billing_chart_tokens: "Token Volume",
      billing_call_list: "Call Details",
      billing_prev_page: "Prev",
      billing_next_page: "Next",
      billing_detail_title: "Call Detail",
      billing_no_data: "No data",
      billing_status_box: "Log Dir",
    },
  };

  const EVENT_LABEL_KEYS = {
    connected: "event_connected",
    run_started: "event_run_started",
    assistant_reason: "event_assistant_reason",
    tool_before: "event_tool_before",
    tool_after: "event_tool_after",
    ask_human: "event_ask_human",
    status: "event_status",
    assistant_delta: "event_assistant_delta",
    run_done: "event_run_done",
    cancel: "event_cancel",
    human_input: "event_human_input",
    file_uploaded: "event_file_uploaded",
  };

  const state = {
    view: "chat",
    lang: localStorage.getItem(LANG_KEY) === "en" ? "en" : "zh",
    sessions: [],
    filter: "all",
    selected: null,
    selectedSessionMsgSig: "",
    messages: [],
    events: [],
    healthOnline: null,
    cronJobs: [],
    heartbeat: null,
    channels: [],
    channelEditor: null,
    skills: [],
    modelState: null,
    modelProfileId: "",
    currentRequestId: "",
    waitingHuman: false,
    liveToolCardByStep: {},
    searchStatus: null,
    searchResults: [],
    searchQuery: "",
    searchLoading: false,
    billingStatus: null,
    billingOverview: null,
    billingCalls: [],
    billingPage: 1,
    billingPageSize: 20,
    billingTotal: 0,
    billingFilters: {
      from_ts: 0,
      to_ts: 0,
      status: "all",
    },
    billingAutoRefreshTimer: null,
    billingAutoRefreshMs: 10000,
    sessionAutoRefreshTimer: null,
    sessionAutoRefreshMs: 1500,
    voiceRecording: false,
    voiceStatusKey: "voice_idle",
    voiceMediaRecorder: null,
    voiceStream: null,
    voiceChunks: [],
  };

  const refs = {
    shellGrid: document.getElementById("shellGrid"),
    langToggleBtn: document.getElementById("langToggleBtn"),
    navItems: document.querySelectorAll(".nav-item"),
    views: {
      chat: document.getElementById("view-chat"),
      search: document.getElementById("view-search"),
      channels: document.getElementById("view-channels"),
      cron: document.getElementById("view-cron"),
      heartbeat: document.getElementById("view-heartbeat"),
      skills: document.getElementById("view-skills"),
      models: document.getElementById("view-models"),
      billing: document.getElementById("view-billing"),
    },
    serviceHealth: document.getElementById("serviceHealth"),
    sessionFilters: document.querySelectorAll(".session-filter"),
    sessionList: document.getElementById("sessionList"),
    newSessionBtn: document.getElementById("newSessionBtn"),
    refreshSessionsBtn: document.getElementById("refreshSessionsBtn"),
    chatTitle: document.getElementById("chatTitle"),
    chatSubtitle: document.getElementById("chatSubtitle"),
    chatMessages: document.getElementById("chatMessages"),
    eventTimeline: document.getElementById("eventTimeline"),
    chatInput: document.getElementById("chatInput"),
    sendBtn: document.getElementById("sendBtn"),
    voiceInputBtn: document.getElementById("voiceInputBtn"),
    voiceInputStatus: document.getElementById("voiceInputStatus"),
    cancelBtn: document.getElementById("cancelBtn"),
    fileInput: document.getElementById("fileInput"),
    reloadChannelsBtn: document.getElementById("reloadChannelsBtn"),
    channelsGrid: document.getElementById("channelsGrid"),
    channelDrawer: document.getElementById("channelDrawer"),
    channelDrawerTitle: document.getElementById("channelDrawerTitle"),
    closeChannelDrawerBtn: document.getElementById("closeChannelDrawerBtn"),
    channelEnabledInput: document.getElementById("channelEnabledInput"),
    channelPrefixInput: document.getElementById("channelPrefixInput"),
    channelFields: document.getElementById("channelFields"),
    channelDrawerHint: document.getElementById("channelDrawerHint"),
    saveChannelBtn: document.getElementById("saveChannelBtn"),
    cancelChannelBtn: document.getElementById("cancelChannelBtn"),
    reloadCronBtn: document.getElementById("reloadCronBtn"),
    cronExpr: document.getElementById("cronExpr"),
    cronUser: document.getElementById("cronUser"),
    cronSession: document.getElementById("cronSession"),
    cronPrompt: document.getElementById("cronPrompt"),
    createCronBtn: document.getElementById("createCronBtn"),
    cronList: document.getElementById("cronList"),
    reloadHeartbeatBtn: document.getElementById("reloadHeartbeatBtn"),
    hbEnabled: document.getElementById("hbEnabled"),
    hbInterval: document.getElementById("hbInterval"),
    hbUser: document.getElementById("hbUser"),
    hbSession: document.getElementById("hbSession"),
    hbPrompt: document.getElementById("hbPrompt"),
    saveHeartbeatBtn: document.getElementById("saveHeartbeatBtn"),
    runHeartbeatBtn: document.getElementById("runHeartbeatBtn"),
    heartbeatState: document.getElementById("heartbeatState"),
    reloadSkillsBtn: document.getElementById("reloadSkillsBtn"),
    skillsGrid: document.getElementById("skillsGrid"),
    newModelBtn: document.getElementById("newModelBtn"),
    reloadModelsBtn: document.getElementById("reloadModelsBtn"),
    modelModal: document.getElementById("modelModal"),
    modelModalTitle: document.getElementById("modelModalTitle"),
    closeModelModalBtn: document.getElementById("closeModelModalBtn"),
    cancelModelModalBtn: document.getElementById("cancelModelModalBtn"),
    modelProfileIdInput: document.getElementById("modelProfileIdInput"),
    modelProviderSelect: document.getElementById("modelProviderSelect"),
    modelBaseUrlInput: document.getElementById("modelBaseUrlInput"),
    modelNameInput: document.getElementById("modelNameInput"),
    modelApiKeyInput: document.getElementById("modelApiKeyInput"),
    modelMaxTokensInput: document.getElementById("modelMaxTokensInput"),
    modelTimeoutInput: document.getElementById("modelTimeoutInput"),
    modelTemperatureInput: document.getElementById("modelTemperatureInput"),
    modelTopPInput: document.getElementById("modelTopPInput"),
    saveModelProfileBtn: document.getElementById("saveModelProfileBtn"),
    modelProfilesGrid: document.getElementById("modelProfilesGrid"),
    modelRuntimeState: document.getElementById("modelRuntimeState"),
    searchInput: document.getElementById("searchInput"),
    searchChannelFilter: document.getElementById("searchChannelFilter"),
    searchLimitInput: document.getElementById("searchLimitInput"),
    runSearchBtn: document.getElementById("runSearchBtn"),
    reindexSearchBtn: document.getElementById("reindexSearchBtn"),
    refreshSearchStatusBtn: document.getElementById("refreshSearchStatusBtn"),
    searchStatusBox: document.getElementById("searchStatusBox"),
    searchResults: document.getElementById("searchResults"),
    refreshBillingBtn: document.getElementById("refreshBillingBtn"),
    billingQuickRange: document.getElementById("billingQuickRange"),
    billingFromInput: document.getElementById("billingFromInput"),
    billingToInput: document.getElementById("billingToInput"),
    billingStatusSelect: document.getElementById("billingStatusSelect"),
    applyBillingFiltersBtn: document.getElementById("applyBillingFiltersBtn"),
    billingStatusBox: document.getElementById("billingStatusBox"),
    billingTotalCalls: document.getElementById("billingTotalCalls"),
    billingSuccessCalls: document.getElementById("billingSuccessCalls"),
    billingFailedCalls: document.getElementById("billingFailedCalls"),
    billingFailureRate: document.getElementById("billingFailureRate"),
    billingPromptTokens: document.getElementById("billingPromptTokens"),
    billingCompletionTokens: document.getElementById("billingCompletionTokens"),
    billingTokensTotal: document.getElementById("billingTokensTotal"),
    billingP95Latency: document.getElementById("billingP95Latency"),
    billingCallsTable: document.getElementById("billingCallsTable"),
    billingPrevBtn: document.getElementById("billingPrevBtn"),
    billingNextBtn: document.getElementById("billingNextBtn"),
    billingPageInfo: document.getElementById("billingPageInfo"),
    billingDetailModal: document.getElementById("billingDetailModal"),
    closeBillingDetailBtn: document.getElementById("closeBillingDetailBtn"),
    billingDetailPre: document.getElementById("billingDetailPre"),
  };

  const t = (key) => I18N[state.lang]?.[key] || I18N.en?.[key] || key;
  const zhen = (zh, en) => (state.lang === "zh" ? zh : en);
  const providerDisplayName = (provider, fallback = "") => {
    const map = {
      openai: zhen("OpenAI", "OpenAI"),
      anthropic: zhen("Anthropic", "Anthropic"),
      dashscope: zhen("DashScope", "DashScope"),
      openai_custom: zhen("OpenAI \u517c\u5bb9\u7aef\u70b9", "OpenAI Compatible Endpoint"),
      anthropic_custom: zhen("Anthropic \u517c\u5bb9\u7aef\u70b9", "Anthropic Compatible Endpoint"),
    };
    return map[provider] || fallback || provider || "-";
  };
  const channelDisplayName = (name, fallback = "") => {
    const key = String(name || "").trim().toLowerCase();
    const map = {
      web: zhen("浏览器", "Browser"),
      cli: zhen("CLI", "CLI"),
      qq: zhen("QQ", "QQ"),
      discord: zhen("Discord", "Discord"),
    };
    return map[key] || fallback || key || "-";
  };
  const channelFieldLabel = (key) => {
    const map = {
      base_url: zhen("访问地址", "Base URL"),
      bind_host: zhen("绑定主机", "Bind Host"),
      port: zhen("端口", "Port"),
      command: zhen("启动命令", "Launch Command"),
      app_id: zhen("App ID", "App ID"),
      client_secret: zhen("Client Secret", "Client Secret"),
      bot_token: zhen("Bot Token", "Bot Token"),
      http_proxy: zhen("HTTP 代理", "HTTP Proxy"),
      http_proxy_auth: zhen("代理认证", "Proxy Auth"),
      application_id: zhen("Application ID", "Application ID"),
      guild_id: zhen("Guild ID", "Guild ID"),
    };
    return map[key] || key;
  };
  const channelRequiredHint = (keys) => {
    const labels = (Array.isArray(keys) ? keys : []).map((k) => channelFieldLabel(k));
    if (!labels.length) return "";
    return zhen(`缺少必填项：${labels.join("、")}`, `Missing required: ${labels.join(", ")}`);
  };
  const esc = (text) =>
    String(text || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  const escapeRegex = (text) => String(text || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  const markdownToSafeHtml = (text) => {
    const raw = String(text || "");
    if (typeof window !== "undefined" && window.marked) {
      try {
        if (window.marked.setOptions) {
          window.marked.setOptions({ gfm: true, breaks: true });
        }
        const html = window.marked.parse(raw);
        if (window.DOMPurify && window.DOMPurify.sanitize) {
          return window.DOMPurify.sanitize(html, { USE_PROFILES: { html: true } });
        }
      } catch {
        // Fall through to escaped plain text below.
      }
    }
    return esc(raw).replaceAll("\n", "<br>");
  };

  const tryParseJson = (value) => {
    try {
      return JSON.parse(value);
    } catch {
      return null;
    }
  };

  const normalizeToolPayload = (raw) => {
    const text = String(raw || "").trim();
    if (!text) return "";

    let parsed = tryParseJson(text);
    if (parsed !== null && typeof parsed === "string") {
      const nested = tryParseJson(parsed);
      parsed = nested === null ? parsed : nested;
    }
    if (parsed === null) return text;

    if (typeof parsed === "string") return parsed;
    try {
      return JSON.stringify(parsed, null, 2);
    } catch {
      return String(parsed);
    }
  };

  const parseToolCalls = (value) => {
    if (Array.isArray(value)) return value;
    if (value && typeof value === "object") return [value];
    if (typeof value === "string") {
      const parsed = tryParseJson(value);
      if (Array.isArray(parsed)) return parsed;
      if (parsed && typeof parsed === "object") return [parsed];
    }
    return [];
  };

  const HIDDEN_CHAT_PREFIXES = [
    "[system message]",
    "[recap plan]",
    "[recap update]",
    "[recap reinject]",
    "[subtask]",
  ];

  const shouldHideConsoleMessage = (value) => {
    const text = String(value || "");
    if (!text.trim()) return false;
    const lowered = text.trimStart().toLowerCase();
    return HIDDEN_CHAT_PREFIXES.some((prefix) => lowered.startsWith(prefix));
  };
  const toolSummaryLabel = (toolName) => `${zhen("\u8c03\u7528\u5de5\u5177", "Tool Call")}: ${toolName || "tool"}`;

  async function api(path, options = {}) {
    const requestOptions = { ...(options || {}) };
    const method = String(requestOptions.method || "GET").trim().toUpperCase();
    requestOptions.cache = "no-store";
    const headers = { ...(requestOptions.headers || {}) };
    headers["Cache-Control"] = "no-cache";
    headers.Pragma = "no-cache";
    requestOptions.headers = headers;

    let finalPath = String(path || "");
    if (method === "GET") {
      const sep = finalPath.includes("?") ? "&" : "?";
      finalPath = `${finalPath}${sep}_ts=${Date.now()}`;
    }

    const response = await fetch(finalPath, requestOptions);
    if (!response.ok) {
      throw new Error((await response.text()) || `${response.status} ${response.statusText}`);
    }
    return response.headers.get("content-type")?.includes("application/json") ? response.json() : response.text();
  }

  function setView(view) {
    state.view = view;
    refs.navItems.forEach((btn) => btn.classList.toggle("active", btn.dataset.view === view));
    Object.entries(refs.views).forEach(([name, el]) => el.classList.toggle("active", name === view));
    refs.shellGrid.classList.toggle("no-sessions", view !== "chat");
    if (view === "chat") {
      startSessionAutoRefresh();
    } else {
      stopSessionAutoRefresh();
    }
    if (view === "billing") {
      startBillingAutoRefresh();
    } else {
      stopBillingAutoRefresh();
    }
  }

  async function loadViewDataOnEnter(view) {
    const name = String(view || "").trim();
    if (!name) return;
    if (name === "search") {
      await loadSearchStatus();
      return;
    }
    if (name === "channels") {
      await loadChannels();
      return;
    }
    if (name === "cron") {
      await loadCron();
      return;
    }
    if (name === "heartbeat") {
      await loadHeartbeat();
      return;
    }
    if (name === "skills") {
      await loadSkills();
      return;
    }
    if (name === "models") {
      await loadModels();
      return;
    }
    if (name === "chat") {
      await refreshSelectedSessionMessages(true);
      return;
    }
    if (name === "billing") {
      // Entering billing should always force latest data and return to page 1.
      await reloadBilling(true);
    }
  }

  function applyI18n() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (key) el.textContent = t(key);
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      if (key) el.setAttribute("placeholder", t(key));
    });
    refs.langToggleBtn.textContent = t("lang_toggle_button");
    refs.langToggleBtn.title = t("lang_toggle_title");
    renderHealth();
    refreshChatHeader();
    renderChannels();
    renderSearchStatus();
    renderSearchResults();
    renderBillingStatus();
    renderBillingOverview();
    renderBillingCalls();
    updateVoiceUi();
    if (state.channelEditor && state.channelEditor.name) {
      openChannelDrawer(state.channelEditor.name);
    }
  }

  function refreshChatHeader() {
    refs.chatTitle.textContent = state.selected ? `${state.selected.channel_prefix.toUpperCase()} / ${state.selected.session_name}` : "Chat";
    refs.chatSubtitle.textContent = state.selected ? state.selected.user_id : t("chat_subtitle_default");
  }

  function renderHealth() {
    refs.serviceHealth.textContent =
      state.healthOnline === null ? t("service_checking") : state.healthOnline ? t("service_online") : t("service_offline");
  }

  const createTextMessageRow = (role, content, streaming = false, allowEmpty = false) => {
    const text = String(content || "");
    if (!allowEmpty && !text.trim()) return null;
    if (text.trim() && shouldHideConsoleMessage(text)) return null;
    const normalizedRole = String(role || "assistant").trim().toLowerCase() || "assistant";
    return {
      role: normalizedRole === "tool" ? "system" : normalizedRole,
      kind: "text",
      content: text,
      streaming: Boolean(streaming),
    };
  };

  const createThinkingMessageRow = (content) => {
    const text = String(content || "").trim();
    if (!text) return null;
    return {
      role: "assistant",
      kind: "thinking",
      content: text,
      streaming: false,
    };
  };

  const createToolCardMessageRow = (toolName, toolCallId = "", inputText = "", outputText = "", streaming = false) => ({
    role: "system",
    kind: "tool_card",
    tool_name: String(toolName || "tool"),
    tool_call_id: String(toolCallId || ""),
    input_text: normalizeToolPayload(inputText),
    output_text: normalizeToolPayload(outputText),
    streaming: Boolean(streaming),
  });

  const pushMessageRow = (rows, row, pendingToolCardsById) => {
    if (!row) return null;
    rows.push(row);
    if (row.kind === "tool_card" && row.tool_call_id) {
      pendingToolCardsById.set(row.tool_call_id, row);
    }
    return row;
  };

  const normalizeRenderMessageRow = (msg) => {
    const kind = String(msg?.kind || "").trim().toLowerCase();
    if (!kind) return null;
    if (kind === "text") {
      return createTextMessageRow(msg.role || "assistant", msg.content || "", Boolean(msg.streaming), Boolean(msg.streaming));
    }
    if (kind === "thinking") {
      return createThinkingMessageRow(msg.content || "");
    }
    if (kind === "tool_card") {
      return createToolCardMessageRow(
        msg.tool_name || msg.name || "tool",
        msg.tool_call_id || msg.toolCallId || "",
        msg.input_text || msg.input || "",
        msg.output_text || msg.output || msg.result || "",
        Boolean(msg.streaming)
      );
    }
    return null;
  };

  const coerceRenderMessageRow = (msg) => {
    if (!msg || typeof msg !== "object") return null;
    const renderRow = normalizeRenderMessageRow(msg);
    if (renderRow) return renderRow;
    const role = String(msg.role || "assistant").trim().toLowerCase() || "assistant";
    return createTextMessageRow(role, msg.content || "", Boolean(msg.streaming), Boolean(msg.streaming && role === "assistant"));
  };

  function normalizeMessages(messages) {
    const rows = Array.isArray(messages) ? messages : [];
    const normalized = [];
    const pendingToolCardsById = new Map();

    rows.forEach((msg) => {
      if (!msg || typeof msg !== "object") return;

      const renderRow = normalizeRenderMessageRow(msg);
      if (renderRow) {
        pushMessageRow(normalized, renderRow, pendingToolCardsById);
        return;
      }

      const role = String(msg.role || "").trim().toLowerCase();

      if (role === "assistant") {
        const calls = parseToolCalls(msg.tool_calls ?? msg.toolCalls ?? msg.toolcalls);
        if (calls.length) {
          pushMessageRow(normalized, createThinkingMessageRow(msg.reasoning_content || ""), pendingToolCardsById);
        }

        pushMessageRow(normalized, createTextMessageRow("assistant", msg.content || "", false), pendingToolCardsById);

        calls.forEach((call) => {
          const fn = call && call.function ? call.function : call && call.func ? call.func : {};
          pushMessageRow(
            normalized,
            createToolCardMessageRow(
              fn.name || call.name || call.tool_name || "tool",
              call.id || call.tool_call_id || call.toolCallId || "",
              fn.arguments || "",
              "",
              false
            ),
            pendingToolCardsById
          );
        });
        return;
      }

      const isToolLike = role === "tool" || Boolean(msg.tool_call_id || msg.toolCallId);
      if (isToolLike) {
        const callId = String(msg.tool_call_id || msg.toolCallId || "");
        const toolName = String(msg.name || msg.tool_name || "tool");
        const output = normalizeToolPayload(msg.content || msg.result || msg.output || "");

        if (callId && pendingToolCardsById.has(callId)) {
          const existing = pendingToolCardsById.get(callId);
          existing.output_text = output;
          if (!existing.tool_name || existing.tool_name === "tool") {
            existing.tool_name = toolName;
          }
        } else {
          pushMessageRow(normalized, createToolCardMessageRow(toolName, callId, "", output, false), pendingToolCardsById);
        }
        return;
      }

      if (role === "user" || role === "system") {
        pushMessageRow(normalized, createTextMessageRow(role, msg.content || "", false), pendingToolCardsById);
      }
    });

    return normalized;
  }

  function buildMessageSignature(messages) {
    const rows = Array.isArray(messages) ? messages : [];
    if (!rows.length) return "0";
    const tail = rows.slice(-3).map((row) => {
      const role = String(row?.role || "");
      const kind = String(row?.kind || "");
      const content = String(row?.content || row?.output_text || row?.input_text || "");
      const key = String(row?.tool_call_id || row?.tool_name || "");
      return `${role}/${kind}/${key}/${content.length}/${content.slice(-80)}`;
    });
    return `${rows.length}|${tail.join("||")}`;
  }

  function renderSessions() {
    refs.sessionList.innerHTML = "";
    const filtered = (state.sessions || []).filter((row) => state.filter === "all" || row.channel_prefix === state.filter);
    if (!filtered.length) {
      refs.sessionList.innerHTML = `<div class="session-item">${esc(t("no_sessions"))}</div>`;
      return;
    }
    filtered.forEach((session) => {
      const active =
        state.selected &&
        state.selected.user_id === session.user_id &&
        state.selected.session_name === session.session_name;
      const badge = ["qq", "cli", "web"].includes(session.channel_prefix) ? session.channel_prefix : "unknown";
      const item = document.createElement("div");
      item.className = `session-item${active ? " active" : ""}`;
      item.innerHTML = `
        <div><span class="badge ${badge}">${esc(session.channel_prefix)}</span> ${esc(session.session_name)}</div>
        <div class="session-meta"><span>${esc(session.user_id)}</span><span>${esc(session.updated_at || "-")}</span></div>
      `;
      item.addEventListener("click", () => selectSession(session));
      refs.sessionList.appendChild(item);
    });
  }

  function renderToolCardMessage(msg) {
    const toolName = String(msg.tool_name || "tool");
    const details = document.createElement("details");
    details.className = "msg system tool-collapse";

    const summary = document.createElement("summary");
    summary.className = "tool-collapse-summary";
    summary.innerHTML = `
      <span class="tool-collapse-title">${esc(toolSummaryLabel(toolName))}</span>
      <span class="tool-collapse-arrow"></span>
    `;
    details.appendChild(summary);

    const body = document.createElement("div");
    body.className = "tool-collapse-body";
    if (msg.input_text) {
      body.innerHTML += `
        <div class="tool-collapse-section">
          <div class="tool-collapse-label">${esc(zhen("\u8f93\u5165", "Input"))}</div>
          <div class="tool-scroll"><pre>${esc(msg.input_text)}</pre></div>
        </div>
      `;
    }
    if (msg.output_text) {
      body.innerHTML += `
        <div class="tool-collapse-section">
          <div class="tool-collapse-label">${esc(zhen("\u8f93\u51fa", "Output"))}</div>
          <div class="tool-scroll"><pre>${esc(msg.output_text)}</pre></div>
        </div>
      `;
    }
    details.appendChild(body);
    return details;
  }

  function renderTextMessage(msg) {
    const role = msg.role === "tool" ? "system" : msg.role;
    const node = document.createElement("div");
    node.className = `msg ${role}`;
    if (role === "assistant" && !msg.streaming) {
      node.classList.add("markdown");
      node.innerHTML = markdownToSafeHtml(msg.content);
    } else {
      node.textContent = msg.content;
    }
    return node;
  }

  function renderThinkingMessage(msg) {
    const node = document.createElement("div");
    node.className = "msg assistant thinking";

    const label = document.createElement("span");
    label.className = "thinking-label";
    label.textContent = "Thinking:";

    const content = document.createElement("span");
    content.className = "thinking-content";
    content.textContent = msg.content;

    node.appendChild(label);
    node.appendChild(content);
    return node;
  }

  function renderMessages() {
    refs.chatMessages.innerHTML = "";
    (state.messages || []).forEach((msg) => {
      const row = coerceRenderMessageRow(msg);
      if (!row) return;

      if (row.kind === "tool_card") {
        refs.chatMessages.appendChild(renderToolCardMessage(row));
        return;
      }

      if (row.kind === "thinking") {
        refs.chatMessages.appendChild(renderThinkingMessage(row));
        return;
      }

      refs.chatMessages.appendChild(renderTextMessage(row));
    });
    refs.chatMessages.scrollTop = refs.chatMessages.scrollHeight;
  }

  function clearEvents() {
    state.events = [];
    state.liveToolCardByStep = {};
    renderEvents();
  }

  function formatPayload(payload) {
    if (!payload) return "";
    if (typeof payload === "string") return payload;
    if (payload.arguments) {
      const args = typeof payload.arguments === "string" ? payload.arguments : JSON.stringify(payload.arguments);
      return `${t("payload_tool")}=${payload.tool_name || ""}\n${t("payload_args")}=${args}`;
    }
    if (payload.state || payload.phase || payload.error) {
      const lines = [];
      if (payload.state) lines.push(`${t("payload_state")}: ${payload.state}`);
      if (payload.phase) lines.push(`${t("payload_phase")}: ${payload.phase}`);
      if (payload.error) lines.push(`${t("payload_error")}: ${payload.error}`);
      if (lines.length) return lines.join("\n");
    }
    if (payload.content) return payload.content;
    if (payload.question) return payload.question;
    return JSON.stringify(payload, null, 2);
  }

  function eventLabel(type) {
    const key = EVENT_LABEL_KEYS[type];
    return key ? t(key) : type;
  }

  function renderEvents(keepBottom = false) {
    refs.eventTimeline.innerHTML = "";
    (state.events || []).forEach((row) => {
      const item = document.createElement("div");
      item.className = `event-item ${row.isError ? "error" : ""}`;
      item.innerHTML = `
        <div class="event-type">${esc(eventLabel(row.type))}</div>
        <div class="event-body">${esc(formatPayload(row.payload))}</div>
      `;
      refs.eventTimeline.appendChild(item);
    });
    if (keepBottom) refs.eventTimeline.scrollTop = refs.eventTimeline.scrollHeight;
  }

  function appendEvent(type, payload, isError = false) {
    state.events.push({ type, payload, isError });
    renderEvents(true);
  }

  function appendMessage(role, content, streaming = false) {
    const row = createTextMessageRow(role, content, streaming, Boolean(streaming));
    if (!row) return;
    state.messages.push(row);
    renderMessages();
  }

  function appendThinkingMessage(content) {
    const row = createThinkingMessageRow(content);
    if (!row) return;
    const last = state.messages[state.messages.length - 1];
    if (last?.kind === "thinking" && String(last.content || "") === row.content) return;
    state.messages.push(row);
    renderMessages();
  }

  function appendToolCardFromEvent(payload) {
    const step = String(payload?.step ?? "");
    const msg = createToolCardMessageRow(payload?.tool_name || "tool", "", payload?.arguments || "", "", false);
    state.messages.push(msg);
    if (step) state.liveToolCardByStep[step] = state.messages.length - 1;
    renderMessages();
  }

  function updateToolCardFromEvent(payload) {
    const step = String(payload?.step ?? "");
    const index = step && Number.isInteger(state.liveToolCardByStep[step]) ? state.liveToolCardByStep[step] : -1;

    let target = null;
    if (index >= 0 && state.messages[index] && state.messages[index].kind === "tool_card") {
      target = state.messages[index];
    } else {
      for (let i = state.messages.length - 1; i >= 0; i -= 1) {
        const row = state.messages[i];
        if (row.kind === "tool_card" && !row.output_text) {
          target = row;
          break;
        }
      }
    }
    if (!target) return;

    const outputValue = payload?.result_preview || payload?.result || payload?.output || payload?.content || payload?.error || "";
    target.output_text = normalizeToolPayload(outputValue);
    renderMessages();
  }

  function appendAssistantDelta(delta) {
    const last = state.messages[state.messages.length - 1];
    if (!last || last.kind !== "text" || last.role !== "assistant" || !last.streaming) {
      state.messages.push(createTextMessageRow("assistant", "", true, true));
    }
    state.messages[state.messages.length - 1].content += delta;
    renderMessages();
  }

  function finalizeStreamingAssistant() {
    const last = state.messages[state.messages.length - 1];
    if (last && last.kind === "text" && last.role === "assistant" && last.streaming) {
      last.streaming = false;
      renderMessages();
    }
  }

  async function loadHealth() {
    try {
      const data = await api("/api/v1/health");
      state.healthOnline = data.success !== false;
    } catch {
      state.healthOnline = false;
    }
    renderHealth();
  }

  async function loadSessions(autoSelect = true) {
    const data = await api("/api/v1/sessions");
    state.sessions = data.sessions || [];
    renderSessions();
    if (autoSelect && !state.selected && state.sessions.length) {
      const preferred = state.sessions.find((s) => s.user_id === "web:local") || state.sessions[0];
      await selectSession(preferred);
    }
  }

  async function selectSession(session) {
    state.selected = {
      user_id: session.user_id,
      session_name: session.session_name,
      channel_prefix: session.channel_prefix,
    };
    state.waitingHuman = false;
    refreshChatHeader();

    await api("/api/v1/sessions/select", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: session.user_id, session_name: session.session_name }),
    });

    state.selectedSessionMsgSig = "";
    await refreshSelectedSessionMessages(true);
    renderSessions();
    clearEvents();
  }

  async function ensureSelectedSession() {
    if (state.selected) return;
    const created = await api("/api/v1/sessions/new", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: "web:local" }),
    });
    await loadSessions(false);
    const target = (state.sessions || []).find(
      (s) => s.user_id === created.session.user_id && s.session_name === created.session.session_name
    );
    if (target) await selectSession(target);
  }

  function onSseEvent(eventName, data) {
    if (eventName === "connected") {
      state.currentRequestId = data.request_id || "";
      appendEvent("connected", data);
      return;
    }
    const payload = data.payload || data;
    switch (eventName) {
      case "run_started":
        state.currentRequestId = payload.request_id || state.currentRequestId;
        appendEvent("run_started", payload);
        break;
      case "assistant_reason":
        appendEvent("assistant_reason", payload);
        appendThinkingMessage(payload.content || payload.reasoning_content || "");
        break;
      case "tool_before":
        appendEvent("tool_before", payload);
        appendToolCardFromEvent(payload);
        break;
      case "tool_after":
        appendEvent("tool_after", payload, Boolean(payload.error));
        updateToolCardFromEvent(payload);
        break;
      case "ask_human":
        state.waitingHuman = true;
        appendEvent("ask_human", payload);
        appendMessage("system", payload.question || t("waiting_input"));
        break;
      case "status":
        appendEvent("status", payload, payload.state === "failed");
        break;
      case "assistant_delta":
        appendAssistantDelta(payload.delta || "");
        break;
      case "run_done":
        finalizeStreamingAssistant();
        state.currentRequestId = "";
        appendEvent("run_done", payload, payload.success === false);
        break;
      default:
        appendEvent(eventName, payload);
        break;
    }
  }

  function handleSseBlock(block) {
    if (!block) return;
    const lines = block.split("\n");
    let eventName = "message";
    let dataRaw = "";
    for (const line of lines) {
      if (line.startsWith("event:")) eventName = line.slice(6).trim();
      if (line.startsWith("data:")) dataRaw += line.slice(5).trim();
    }
    let data = {};
    try {
      data = dataRaw ? JSON.parse(dataRaw) : {};
    } catch {
      data = { raw: dataRaw };
    }
    onSseEvent(eventName, data);
  }

  async function streamChat(content) {
    const response = await fetch("/api/v1/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        request_id: "",
        user_id: state.selected.user_id,
        session_name: state.selected.session_name,
        content,
        continue_mode: "in_place",
        source: "web",
        inject_uploaded_files: true,
      }),
    });
    if (!response.ok || !response.body) {
      throw new Error((await response.text()) || t("stream_failed"));
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split("\n\n");
      buffer = blocks.pop() || "";
      blocks.forEach((block) => handleSseBlock(block.trim()));
    }
    if (buffer.trim()) handleSseBlock(buffer.trim());
    finalizeStreamingAssistant();
    await loadSessions(false);
    await refreshSelectedSessionMessages(true);
  }

  async function sendMessage() {
    const content = refs.chatInput.value.trim();
    if (!content) return;
    await ensureSelectedSession();
    if (!state.selected) return;
    refs.chatInput.value = "";

    if (state.waitingHuman) {
      await api("/api/v1/chat/human-input", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: state.selected.user_id, content }),
      });
      appendMessage("user", content);
      state.waitingHuman = false;
      appendEvent("human_input", { content: t("human_input_submitted") });
      return;
    }

    appendMessage("user", content);
    await streamChat(content);
  }

  async function cancelCurrent() {
    if (!state.currentRequestId) return;
    await api("/api/v1/chat/cancel", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ request_id: state.currentRequestId }),
    });
    appendEvent("cancel", { request_id: state.currentRequestId });
  }

  async function uploadFile(file) {
    await ensureSelectedSession();
    const form = new FormData();
    form.append("file", file);
    form.append("user_id", state.selected ? state.selected.user_id : "web:local");
    const response = await fetch("/api/v1/files/upload", { method: "POST", body: form });
    if (!response.ok) throw new Error(await response.text());
    const data = await response.json();
    appendEvent("file_uploaded", data.file || {});
  }

  function pickVoiceMimeType() {
    const candidates = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/mp4",
    ];
    if (typeof MediaRecorder === "undefined" || typeof MediaRecorder.isTypeSupported !== "function") {
      return "";
    }
    for (const mime of candidates) {
      try {
        if (MediaRecorder.isTypeSupported(mime)) return mime;
      } catch {
        // Ignore and continue.
      }
    }
    return "";
  }

  function updateVoiceUi() {
    if (refs.voiceInputBtn) {
      refs.voiceInputBtn.textContent = state.voiceRecording ? t("btn_voice_stop") : t("btn_voice_start");
      refs.voiceInputBtn.classList.toggle("voice-recording", Boolean(state.voiceRecording));
    }
    if (refs.voiceInputStatus) {
      refs.voiceInputStatus.textContent = t(state.voiceStatusKey || "voice_idle");
      refs.voiceInputStatus.classList.toggle("recording", Boolean(state.voiceRecording));
    }
  }

  function cleanupVoiceStream() {
    const stream = state.voiceStream;
    state.voiceStream = null;
    if (!stream) return;
    try {
      stream.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch {
          // Ignore cleanup errors.
        }
      });
    } catch {
      // Ignore cleanup errors.
    }
  }

  async function transcribeVoiceBlob(blob, mimeType) {
    if (!blob || !blob.size) {
      state.voiceStatusKey = "voice_empty";
      updateVoiceUi();
      return;
    }
    state.voiceStatusKey = "voice_transcribing";
    updateVoiceUi();

    const ext = mimeType && mimeType.includes("ogg") ? "ogg" : mimeType && mimeType.includes("mp4") ? "m4a" : "webm";
    const form = new FormData();
    form.append("file", blob, `voice_input.${ext}`);
    form.append("language", "auto");
    form.append("task", "transcribe");

    const response = await fetch("/api/v1/speech/transcribe", {
      method: "POST",
      body: form,
    });
    if (!response.ok) {
      throw new Error((await response.text()) || "speech transcribe failed");
    }
    const data = await response.json();
    const text = String((data.result || {}).text || "").trim();
    if (!text) {
      state.voiceStatusKey = "voice_empty";
      updateVoiceUi();
      return;
    }

    const current = String(refs.chatInput?.value || "");
    refs.chatInput.value = current ? `${current}\n${text}` : text;
    state.voiceStatusKey = "voice_transcribed";
    updateVoiceUi();
  }

  async function startVoiceInput() {
    if (state.voiceRecording) return;
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || typeof MediaRecorder === "undefined") {
      state.voiceStatusKey = "voice_unsupported";
      updateVoiceUi();
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = pickVoiceMimeType();
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      state.voiceStream = stream;
      state.voiceMediaRecorder = recorder;
      state.voiceChunks = [];

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          state.voiceChunks.push(event.data);
        }
      };

      recorder.onerror = () => {
        state.voiceRecording = false;
        state.voiceStatusKey = "voice_idle";
        cleanupVoiceStream();
        updateVoiceUi();
      };

      recorder.onstop = async () => {
        const chunks = Array.isArray(state.voiceChunks) ? state.voiceChunks.slice() : [];
        state.voiceChunks = [];
        const finalMime = recorder.mimeType || mimeType || "audio/webm";
        state.voiceMediaRecorder = null;
        cleanupVoiceStream();
        state.voiceRecording = false;
        updateVoiceUi();

        try {
          const blob = new Blob(chunks, { type: finalMime });
          await transcribeVoiceBlob(blob, finalMime);
        } catch (err) {
          state.voiceStatusKey = "voice_idle";
          updateVoiceUi();
          alert(`${t("action_failed")}: ${err}`);
        }
      };

      recorder.start(250);
      state.voiceRecording = true;
      state.voiceStatusKey = "voice_recording";
      updateVoiceUi();
    } catch (err) {
      const message = String(err || "").toLowerCase();
      state.voiceStatusKey = message.includes("denied") || message.includes("notallowed") ? "voice_permission_denied" : "voice_idle";
      updateVoiceUi();
      if (state.voiceStatusKey === "voice_permission_denied") {
        alert(t("voice_permission_denied"));
      } else {
        alert(`${t("action_failed")}: ${err}`);
      }
    }
  }

  function stopVoiceInput() {
    const recorder = state.voiceMediaRecorder;
    if (!recorder) return;
    try {
      if (recorder.state === "recording") {
        recorder.stop();
      }
    } catch (err) {
      cleanupVoiceStream();
      state.voiceRecording = false;
      state.voiceStatusKey = "voice_idle";
      updateVoiceUi();
      throw err;
    }
  }

  function toggleVoiceInput() {
    if (state.voiceRecording) {
      stopVoiceInput();
      return;
    }
    startVoiceInput().catch((err) => {
      state.voiceStatusKey = "voice_idle";
      updateVoiceUi();
      alert(`${t("action_failed")}: ${err}`);
    });
  }

  function renderCron() {
    refs.cronList.innerHTML = "";
    const jobs = state.cronJobs || [];
    if (!jobs.length) {
      refs.cronList.textContent = t("no_cron_jobs");
      return;
    }
    jobs.forEach((job) => {
      const row = document.createElement("div");
      row.className = "table-row";
      row.innerHTML = `
        <div><b>${esc(job.id)}</b></div>
        <div>${t("cron_expr_label")}: ${esc(job.cron_expr)}</div>
        <div>${t("target_label")}: ${esc(job.user_id)} :: ${esc(job.session_name || "-")}</div>
        <div>${t("status_label")}: ${esc(job.last_status || "never")} / ${t("paused_label")}=${String(job.paused)}</div>
        <div>${t("next_run_label")}: ${esc(String(job.next_run_ts || "-"))}</div>
        <div>${t("last_run_label")}: ${esc(job.last_run_at || "-")}</div>
        <div>${t("last_result_label")}: ${esc(job.last_result || "")}</div>
      `;
      const actions = document.createElement("div");
      actions.className = "row-actions";
      actions.append(
        makeActionBtn(job.paused ? t("btn_resume") : t("btn_pause"), async () => {
          await api(`/api/v1/cron/jobs/${encodeURIComponent(job.id)}/${job.paused ? "resume" : "pause"}`, { method: "POST" });
          await loadCron();
        }),
        makeActionBtn(t("btn_run"), async () => {
          await api(`/api/v1/cron/jobs/${encodeURIComponent(job.id)}/run`, { method: "POST" });
          await loadCron();
        }),
        makeActionBtn(t("btn_delete"), async () => {
          await api(`/api/v1/cron/jobs/${encodeURIComponent(job.id)}`, { method: "DELETE" });
          await loadCron();
        })
      );
      row.appendChild(actions);
      refs.cronList.appendChild(row);
    });
  }

  async function loadCron() {
    state.cronJobs = (await api("/api/v1/cron/jobs")).jobs || [];
    renderCron();
  }

  async function createCron() {
    await api("/api/v1/cron/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        cron_expr: refs.cronExpr.value.trim(),
        user_id: refs.cronUser.value.trim() || "web:local",
        session_name: refs.cronSession.value.trim(),
        prompt: refs.cronPrompt.value.trim(),
      }),
    });
    refs.cronPrompt.value = "";
    await loadCron();
  }

  function renderHeartbeat() {
    const hb = state.heartbeat || {};
    refs.hbEnabled.checked = Boolean(hb.enabled);
    refs.hbInterval.value = hb.interval_seconds || 1800;
    refs.hbUser.value = hb.user_id || "web:local";
    refs.hbSession.value = hb.session_name || "";
    refs.hbPrompt.value = hb.prompt || "";
    refs.heartbeatState.textContent =
      `${t("hb_state_last_run")}: ${hb.last_run_at || "-"}\n` +
      `${t("hb_state_last_status")}: ${hb.last_status || "-"}\n` +
      `${t("hb_state_last_result")}: ${hb.last_result || ""}`;
  }

  async function loadHeartbeat() {
    state.heartbeat = (await api("/api/v1/heartbeat")).heartbeat || {};
    renderHeartbeat();
  }

  async function saveHeartbeat() {
    await api("/api/v1/heartbeat", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        enabled: refs.hbEnabled.checked,
        interval_seconds: Number(refs.hbInterval.value || 1800),
        user_id: refs.hbUser.value.trim() || "web:local",
        session_name: refs.hbSession.value.trim(),
        prompt: refs.hbPrompt.value.trim(),
      }),
    });
    await loadHeartbeat();
  }

  async function runHeartbeat() {
    await api("/api/v1/heartbeat/run", { method: "POST" });
    setTimeout(loadHeartbeat, 300);
  }

  function channelStatusText(row) {
    if (!row || !row.enabled) return zhen("已禁用", "Disabled");
    if (row.ready) return zhen("已启用", "Enabled");
    return zhen("配置不完整", "Config Incomplete");
  }

  function channelStatusClass(row) {
    if (!row || !row.enabled) return "disabled";
    if (row.ready) return "enabled";
    return "error";
  }

  function summarizeChannel(row) {
    if (!row) return "-";
    const settings = {};
    (row.fields || []).forEach((field) => {
      settings[field.key] = field.secret ? (field.has_value ? "••••••" : "") : String(field.value || "");
    });
    if (row.name === "web") return settings.base_url || row.launch_hint || "-";
    if (row.name === "cli") return settings.command || row.launch_hint || "-";
    if (row.name === "qq") return settings.app_id ? `app_id=${settings.app_id}` : row.launch_hint || "-";
    if (row.name === "discord") {
      if (settings.guild_id) return `guild_id=${settings.guild_id}`;
      if (settings.http_proxy) return `proxy=${settings.http_proxy}`;
      return row.launch_hint || "-";
    }
    return row.launch_hint || "-";
  }

  function renderChannels() {
    if (!refs.channelsGrid) return;
    refs.channelsGrid.innerHTML = "";
    const rows = state.channels || [];
    if (!rows.length) {
      refs.channelsGrid.textContent = t("no_channels");
      return;
    }
    rows.forEach((row) => {
      const card = document.createElement("div");
      card.className = "channel-card";
      const statusClass = channelStatusClass(row);
      const missingText = row.enabled && !row.ready ? channelRequiredHint(row.missing_required || []) : "";
      card.innerHTML = `
        <div class="channel-head">
          <span class="channel-status ${statusClass}">${esc(channelStatusText(row))}</span>
          <span class="channel-tag">${esc(channelDisplayName(row.name, row.display_name || row.name))}</span>
        </div>
        <h3 class="channel-title">${esc(channelDisplayName(row.name, row.display_name || row.name))}</h3>
        <div class="channel-desc">${esc(row.description || "-")}</div>
        <div class="channel-meta">${esc(summarizeChannel(row))}</div>
        <div class="channel-meta">${esc(missingText || (row.bot_prefix ? `prefix=${row.bot_prefix}` : row.launch_hint || ""))}</div>
      `;
      card.addEventListener("click", () => openChannelDrawer(row.name));
      refs.channelsGrid.appendChild(card);
    });
  }

  function openChannelDrawer(channelName) {
    if (!refs.channelDrawer) return;
    const target = (state.channels || []).find((row) => row.name === channelName);
    if (!target) return;
    state.channelEditor = JSON.parse(JSON.stringify(target));
    refs.channelEnabledInput.checked = Boolean(state.channelEditor.enabled);
    refs.channelPrefixInput.value = String(state.channelEditor.bot_prefix || "");
    refs.channelDrawerTitle.textContent = `${channelDisplayName(target.name, target.display_name || target.name)} ${zhen("设置", "Settings")}`;

    refs.channelFields.innerHTML = "";
    (state.channelEditor.fields || []).forEach((field) => {
      const wrap = document.createElement("label");
      wrap.className = "channel-field";
      const requiredMark = field.required ? " *" : "";
      const hint = field.secret && field.has_value ? zhen("已配置，留空不改", "configured, blank keeps current") : (field.placeholder || "");
      const type = field.type === "number" ? "number" : (field.secret ? "password" : "text");
      wrap.innerHTML = `
        <span>${esc(channelFieldLabel(field.key))}${requiredMark}</span>
        <input
          type="${type}"
          data-channel-key="${esc(field.key)}"
          data-channel-secret="${field.secret ? "1" : "0"}"
          value="${field.secret ? "" : esc(String(field.value || ""))}"
          placeholder="${esc(hint)}"
        />
      `;
      refs.channelFields.appendChild(wrap);
    });

    const missing = state.channelEditor.missing_required || [];
    refs.channelDrawerHint.textContent = missing.length ? channelRequiredHint(missing) : (target.launch_hint || "");
    refs.channelDrawer.classList.remove("hidden");
  }

  function closeChannelDrawer() {
    if (!refs.channelDrawer) return;
    state.channelEditor = null;
    refs.channelDrawer.classList.add("hidden");
  }

  async function loadChannels() {
    state.channels = (await api("/api/v1/channels")).channels || [];
    renderChannels();
  }

  async function saveChannelConfig() {
    if (!state.channelEditor || !refs.channelFields) return;
    const settings = {};
    refs.channelFields.querySelectorAll("input[data-channel-key]").forEach((input) => {
      const key = input.getAttribute("data-channel-key");
      const secret = input.getAttribute("data-channel-secret") === "1";
      const text = String(input.value || "").trim();
      if (!key) return;
      if (secret && !text) return;
      settings[key] = text;
    });

    const payload = {
      enabled: refs.channelEnabledInput.checked,
      bot_prefix: refs.channelPrefixInput.value.trim(),
      settings,
    };
    const response = await api(`/api/v1/channels/${encodeURIComponent(state.channelEditor.name)}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    state.channels = response.channels || [];
    closeChannelDrawer();
    renderChannels();
  }

  function renderSkills() {
    refs.skillsGrid.innerHTML = "";
    const rows = state.skills || [];
    if (!rows.length) {
      refs.skillsGrid.textContent = t("no_skills");
      return;
    }
    rows.forEach((skill) => {
      const card = document.createElement("div");
      card.className = "skill-card";
      card.innerHTML = `
        <div class="skill-head"><h3 class="skill-title">${esc(skill.name || skill.directory || "")}</h3></div>
        <div class="skill-body">${esc(skill.description || "-")}</div>
        <div class="skill-path"><b>${t("skill_path")}:</b> ${esc(skill.path || "-")}</div>
      `;
      refs.skillsGrid.appendChild(card);
    });
  }

  async function loadSkills() {
    state.skills = (await api("/api/v1/skills")).skills || [];
    renderSkills();
  }

  function renderSearchStatus() {
    if (!refs.searchStatusBox) return;
    const status = state.searchStatus;
    if (!status) {
      refs.searchStatusBox.textContent = `${t("search_status_ready")}: -`;
      return;
    }
    refs.searchStatusBox.textContent =
      `${t("search_status_ready")}: ${status.ready ? "yes" : "no"}\n` +
      `${t("search_status_indexing")}: ${status.indexing ? "yes" : "no"}\n` +
      `${t("search_status_last_index")}: ${status.last_indexed_at || "-"}\n` +
      `${t("search_status_chunks")}: ${status.chunks ?? 0}\n` +
      `${t("search_status_files")}: ${status.files ?? 0}\n` +
      `${t("search_status_embedder")}: ${status.embedder || "-"}\n` +
      `DB: ${status.db_path || "-"}`;
  }

  function markPreviewByQuery(preview, query) {
    const text = String(preview || "");
    const q = String(query || "").trim();
    if (!q) return esc(text);
    const tokens = [...new Set(q.split(/\s+/).map((x) => x.trim()).filter((x) => x.length >= 2))].slice(0, 8);
    if (!tokens.length) return esc(text);
    const pattern = new RegExp(`(${tokens.map((x) => escapeRegex(x)).join("|")})`, "ig");
    const marked = text.replace(pattern, "@@ANGEL_HL_START@@$1@@ANGEL_HL_END@@");
    return esc(marked)
      .replaceAll("@@ANGEL_HL_START@@", '<span class="search-hit-mark">')
      .replaceAll("@@ANGEL_HL_END@@", "</span>");
  }

  function renderSearchResults() {
    if (!refs.searchResults) return;
    refs.searchResults.innerHTML = "";
    if (state.searchLoading) {
      refs.searchResults.innerHTML = `<div class="search-empty">${esc(zhen("检索中...", "Searching..."))}</div>`;
      return;
    }
    const rows = state.searchResults || [];
    if (!rows.length) {
      refs.searchResults.innerHTML = `<div class="search-empty">${esc(t("search_no_results"))}</div>`;
      return;
    }

    rows.forEach((hit) => {
      const card = document.createElement("article");
      card.className = "search-hit";
      const score = Number(hit.score || 0).toFixed(4);
      const channel = String(hit.channel_prefix || "unknown");
      const matchedBy = Array.isArray(hit.matched_by) ? hit.matched_by.join(" + ") : "-";
      card.innerHTML = `
        <div class="search-hit-top">
          <h3 class="search-hit-title">${esc(hit.session_name || "-")}</h3>
          <span class="badge ${esc(channel)}">${esc(channel)}</span>
        </div>
        <div class="search-hit-meta">
          <span>${esc(hit.user_id || "-")}</span>
          <span>${esc(t("search_score"))}: ${esc(score)}</span>
          <span>match=${esc(matchedBy || "-")}</span>
        </div>
        <div class="search-hit-preview">${markPreviewByQuery(hit.preview || "", state.searchQuery)}</div>
      `;

      card.addEventListener("click", () => {
        openSearchHit(hit).catch((err) => alert(`${t("action_failed")}: ${err}`));
      });

      refs.searchResults.appendChild(card);
    });
  }

  async function loadSearchStatus() {
    const data = await api("/api/v1/search/status");
    state.searchStatus = data.status || null;
    renderSearchStatus();
  }

  async function runSearch() {
    const q = String(refs.searchInput?.value || "").trim();
    if (!q) {
      state.searchQuery = "";
      state.searchResults = [];
      renderSearchResults();
      return;
    }

    const limitRaw = Number(refs.searchLimitInput?.value || 20);
    const limit = Number.isFinite(limitRaw) ? Math.max(1, Math.min(100, Math.round(limitRaw))) : 20;
    const channel = String(refs.searchChannelFilter?.value || "").trim();

    state.searchQuery = q;
    state.searchLoading = true;
    renderSearchResults();
    const qs = new URLSearchParams({ q, limit: String(limit) });
    if (channel) qs.set("channel", channel);

    try {
      const data = await api(`/api/v1/search/sessions?${qs.toString()}`);
      const result = data.result || {};
      state.searchResults = Array.isArray(result.session_hits) ? result.session_hits : [];
    } finally {
      state.searchLoading = false;
      renderSearchResults();
    }
  }

  async function reindexSearch() {
    state.searchLoading = true;
    renderSearchResults();
    try {
      await api("/api/v1/search/reindex", { method: "POST" });
      await loadSearchStatus();
      await runSearch();
    } finally {
      state.searchLoading = false;
      renderSearchResults();
    }
  }

  async function openSearchHit(hit) {
    if (!hit) return;
    const target = {
      user_id: hit.user_id,
      session_name: hit.session_name,
      channel_prefix: hit.channel_prefix || "unknown",
    };
    setView("chat");
    await loadSessions(false);
    await selectSession(target);
  }

  function toLocalInputValue(unixTs) {
    const ts = Number(unixTs || 0);
    if (!Number.isFinite(ts) || ts <= 0) return "";
    const d = new Date(ts * 1000);
    const pad = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  function fromLocalInputValue(value, fallback = 0, endOfMinute = false) {
    const text = String(value || "").trim();
    if (!text) return fallback;
    const ms = Date.parse(text);
    if (!Number.isFinite(ms)) return fallback;
    const base = Math.floor(ms / 1000);
    // datetime-local is often minute-precision (YYYY-MM-DDTHH:mm).
    // For end bounds, include the whole minute to avoid excluding recent records.
    if (endOfMinute && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(text)) {
      return base + 59;
    }
    return base;
  }

  function formatNum(value) {
    const n = Number(value || 0);
    const locale = state.lang === "zh" ? "zh-CN" : "en-US";
    return new Intl.NumberFormat(locale).format(Number.isFinite(n) ? n : 0);
  }

  function formatTs(ts) {
    const n = Number(ts || 0);
    if (!Number.isFinite(n) || n <= 0) return "-";
    return new Date(n * 1000).toLocaleString(state.lang === "zh" ? "zh-CN" : "en-US");
  }

  function applyBillingQuickRange(rangeValue) {
    const key = String(rangeValue || refs.billingQuickRange?.value || "12h");
    const now = Math.floor(Date.now() / 1000);
    let fromTs = now - 12 * 3600;
    if (key === "24h") fromTs = now - 24 * 3600;
    if (key === "7d") fromTs = now - 7 * 24 * 3600;
    if (key === "30d") fromTs = now - 30 * 24 * 3600;
    if (key === "custom") return;
    refs.billingFromInput.value = toLocalInputValue(fromTs);
    refs.billingToInput.value = toLocalInputValue(now);
  }

  function shouldAutoShiftBillingWindow() {
    const key = String(refs.billingQuickRange?.value || "12h").trim().toLowerCase();
    return key !== "custom";
  }

  function readBillingFilters(resetPage = false) {
    let fromTs = 0;
    let toTs = 0;
    const now = Math.floor(Date.now() / 1000);

    if (shouldAutoShiftBillingWindow()) {
      const key = String(refs.billingQuickRange?.value || "12h").trim().toLowerCase();
      let span = 12 * 3600;
      if (key === "24h") span = 24 * 3600;
      if (key === "7d") span = 7 * 24 * 3600;
      if (key === "30d") span = 30 * 24 * 3600;
      fromTs = now - span;
      toTs = now;
      // Keep UI fields in sync (display only; true query window remains second-precision).
      refs.billingFromInput.value = toLocalInputValue(fromTs);
      refs.billingToInput.value = toLocalInputValue(toTs);
    } else {
      const defaultFrom = now - 12 * 3600;
      fromTs = fromLocalInputValue(refs.billingFromInput?.value, defaultFrom, false);
      toTs = fromLocalInputValue(refs.billingToInput?.value, now, true);
    }

    state.billingFilters = {
      from_ts: Math.min(fromTs, toTs),
      to_ts: Math.max(fromTs, toTs),
      status: String(refs.billingStatusSelect?.value || "all").trim() || "all",
    };
    if (resetPage) state.billingPage = 1;
    return state.billingFilters;
  }

  function stopBillingAutoRefresh() {
    if (state.billingAutoRefreshTimer) {
      clearInterval(state.billingAutoRefreshTimer);
      state.billingAutoRefreshTimer = null;
    }
  }

  function startBillingAutoRefresh() {
    stopBillingAutoRefresh();
    if (state.view !== "billing") return;
    state.billingAutoRefreshTimer = setInterval(() => {
      if (state.view !== "billing") return;
      reloadBilling(false).catch((err) => {
        console.warn("billing auto refresh failed", err);
      });
    }, Number(state.billingAutoRefreshMs || 10000));
  }

  function billingQueryParams(withPaging = false) {
    const f = state.billingFilters || {};
    const qs = new URLSearchParams({
      from_ts: String(f.from_ts || 0),
      to_ts: String(f.to_ts || 0),
      status: String(f.status || "all"),
    });
    if (withPaging) {
      qs.set("page", String(state.billingPage || 1));
      qs.set("page_size", "20");
    }
    return qs;
  }

  function renderBillingStatus() {
    if (!refs.billingStatusBox) return;
    const row = state.billingStatus;
    if (!row) {
      refs.billingStatusBox.textContent = `${t("billing_status_box")}: -`;
      return;
    }
    refs.billingStatusBox.textContent =
      `${t("billing_status_box")}: ${row.log_dir || "-"}\n` +
      `${zhen("可读天数", "Readable Days")}: ${formatNum(row.readable_days || 0)}\n` +
      `${zhen("总记录数", "Total Records")}: ${formatNum(row.total_records || 0)}\n` +
      `${zhen("最近写入", "Last Write")}: ${formatTs(row.last_write_at || 0)}\n` +
      `${zhen("写入错误", "Writer Errors")}: ${formatNum(row.writer_errors || 0)}`;
  }

  function renderBillingOverview() {
    const overviewNode = state.billingOverview || {};
    const row = overviewNode.overview || {};

    if (refs.billingTotalCalls) refs.billingTotalCalls.textContent = formatNum(row.total_calls || 0);
    if (refs.billingSuccessCalls) refs.billingSuccessCalls.textContent = formatNum(row.success_calls || 0);
    if (refs.billingFailedCalls) refs.billingFailedCalls.textContent = formatNum(row.failed_calls || 0);
    if (refs.billingFailureRate) refs.billingFailureRate.textContent = `${Number(row.failure_rate || 0).toFixed(2)}%`;
    if (refs.billingPromptTokens) refs.billingPromptTokens.textContent = formatNum(row.prompt_tokens_total || 0);
    if (refs.billingCompletionTokens) refs.billingCompletionTokens.textContent = formatNum(row.completion_tokens_total || 0);
    if (refs.billingTokensTotal) refs.billingTokensTotal.textContent = formatNum(row.tokens_total || 0);
    if (refs.billingP95Latency) refs.billingP95Latency.textContent = `${formatNum(row.p95_latency_ms || 0)}ms`;
  }

  function renderBillingCalls() {
    if (!refs.billingCallsTable) return;
    refs.billingCallsTable.innerHTML = "";
    const rows = Array.isArray(state.billingCalls) ? state.billingCalls : [];
    const totalPages = Math.max(1, Math.ceil((state.billingTotal || 0) / 20));
    const currentPage = Math.max(1, Math.min(totalPages, Number(state.billingPage || 1)));
    state.billingPage = currentPage;
    state.billingPageSize = 20;
    if (!rows.length) {
      refs.billingCallsTable.innerHTML = `<div class="billing-row"><div class="billing-row-preview">${esc(t("billing_no_data"))}</div></div>`;
      if (refs.billingPageInfo) refs.billingPageInfo.textContent = `1 / 1`;
      if (refs.billingPrevBtn) refs.billingPrevBtn.disabled = true;
      if (refs.billingNextBtn) refs.billingNextBtn.disabled = true;
      return;
    }

    rows.forEach((row) => {
      const node = document.createElement("div");
      node.className = "billing-row";
      const ok = Boolean(row.success);
      node.innerHTML = `
        <div class="billing-row-top">
          <div class="billing-row-title">${esc(row.provider || "-")} / ${esc(row.model || "-")}</div>
          <span class="billing-status-pill ${ok ? "success" : "failed"}">${esc(ok ? t("billing_status_success") : t("billing_status_failed"))}</span>
        </div>
        <div class="billing-row-meta">
          <span>id=${esc(row.call_id || "-")}</span>
          <span>${formatTs(row.started_at)}</span>
          <span>lat=${esc(row.latency_ms || 0)}ms</span>
          <span>tokens=${esc(row.total_tokens || 0)}</span>
          <span>prompt=${esc(row.prompt_tokens || 0)}</span>
          <span>completion=${esc(row.completion_tokens || 0)}</span>
          <span>src=${esc(row.usage_source || "-")}</span>
          <span>profile=${esc(row.profile_id || "-")}</span>
        </div>
        <div class="billing-row-preview">${esc(row.input_preview || row.error_message || "")}</div>
      `;
      node.addEventListener("click", () => {
        openBillingDetail(row.call_id).catch((err) => alert(`${t("action_failed")}: ${err}`));
      });
      refs.billingCallsTable.appendChild(node);
    });

    if (refs.billingPageInfo) refs.billingPageInfo.textContent = `${currentPage} / ${totalPages}`;
    if (refs.billingPrevBtn) refs.billingPrevBtn.disabled = currentPage <= 1;
    if (refs.billingNextBtn) refs.billingNextBtn.disabled = currentPage >= totalPages;
  }

  async function loadBillingStatus() {
    const data = await api("/api/v1/billing/status");
    state.billingStatus = data.status || null;
    renderBillingStatus();
  }

  async function loadBillingOverview() {
    const qs = billingQueryParams(false);
    const data = await api(`/api/v1/billing/overview?${qs.toString()}`);
    state.billingOverview = data.result || null;
    renderBillingOverview();
  }

  async function loadBillingCalls() {
    const qs = billingQueryParams(true);
    const data = await api(`/api/v1/billing/calls?${qs.toString()}`);
    const result = data.result || {};
    state.billingCalls = Array.isArray(result.items) ? result.items.slice(0, 20) : [];
    state.billingTotal = Number(result.total || 0);
    state.billingPage = Math.max(1, Number(result.page || state.billingPage || 1));
    state.billingPageSize = 20;
    renderBillingCalls();
  }

  async function reloadBilling(resetPage = false) {
    readBillingFilters(resetPage);
    await loadBillingStatus();
    await loadBillingOverview();
    await loadBillingCalls();
  }

  async function openBillingDetail(callId) {
    const cid = String(callId || "").trim();
    if (!cid) return;
    const data = await api(`/api/v1/billing/calls/${encodeURIComponent(cid)}`);
    const detail = data.detail || {};
    if (refs.billingDetailPre) {
      refs.billingDetailPre.textContent = JSON.stringify(detail, null, 2);
    }
    refs.billingDetailModal.classList.remove("hidden");
  }

  function closeBillingDetail() {
    if (!refs.billingDetailModal) return;
    refs.billingDetailModal.classList.add("hidden");
  }

  const getProfiles = () => (state.modelState && state.modelState.profiles) || [];
  const getProviderCatalog = () => (state.modelState && state.modelState.providers) || [];
  const getProviderPreset = (providerName) => getProviderCatalog().find((row) => row.provider === providerName) || null;

  const parseOptionalNumber = (raw, fieldName) => {
    const text = String(raw || "").trim();
    if (!text) return null;
    const value = Number(text);
    if (Number.isNaN(value)) throw new Error(`${fieldName} must be a number`);
    return value;
  };

  const randomCode = (length = 8) => {
    const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
    const n = Math.max(4, Number(length) || 8);
    if (typeof window !== "undefined" && window.crypto && window.crypto.getRandomValues) {
      const bytes = new Uint8Array(n);
      window.crypto.getRandomValues(bytes);
      return Array.from(bytes)
        .map((b) => chars[b % chars.length])
        .join("");
    }
    let out = "";
    for (let i = 0; i < n; i += 1) {
      out += chars[Math.floor(Math.random() * chars.length)];
    }
    return out;
  };

  const buildDefaultProfileId = () => `default_${randomCode(8)}`;

  function resetModelModal() {
    refs.modelProfileIdInput.value = buildDefaultProfileId();
    refs.modelApiKeyInput.value = "";
    refs.modelMaxTokensInput.value = "";
    refs.modelTimeoutInput.value = "";
    refs.modelTemperatureInput.value = "";
    refs.modelTopPInput.value = "";
    renderModelProviderSelect("");
    const first = getProviderCatalog()[0];
    if (first) {
      refs.modelProviderSelect.value = first.provider;
      applyProviderPreset(first.provider, true);
    } else {
      refs.modelBaseUrlInput.value = "";
      refs.modelNameInput.value = "";
    }
    refreshModelModalText();
  }

  function openModelModal() {
    resetModelModal();
    refs.modelModal.classList.remove("hidden");
  }

  function closeModelModal() {
    refs.modelModal.classList.add("hidden");
  }

  function refreshModelModalText() {
    refs.modelModalTitle.textContent = zhen("新建模型", "Create Model");
    refs.closeModelModalBtn.textContent = zhen("关闭", "Close");
  }

  function renderModelProviderSelect(selected) {
    const providers = getProviderCatalog();
    refs.modelProviderSelect.innerHTML = "";
    providers.forEach((row) => {
      const opt = document.createElement("option");
      opt.value = row.provider;
      opt.textContent = providerDisplayName(row.provider, row.display_name || row.provider);
      refs.modelProviderSelect.appendChild(opt);
    });
    if (selected && providers.some((p) => p.provider === selected)) {
      refs.modelProviderSelect.value = selected;
    } else if (providers.length) {
      refs.modelProviderSelect.value = providers[0].provider;
    }
  }

  function applyProviderPreset(providerName, forceFill = false) {
    const preset = getProviderPreset(providerName);
    if (!preset) return;
    const isCustom = Boolean(preset.is_custom);
    const presetBase = isCustom ? "" : preset.default_base_url || "";
    const presetModel = preset.default_model || "";

    if (forceFill || !refs.modelBaseUrlInput.value.trim() || isCustom) {
      refs.modelBaseUrlInput.value = presetBase;
    }
    if (forceFill || !refs.modelNameInput.value.trim()) {
      refs.modelNameInput.value = presetModel;
    }
  }

  const connectivityClass = (status) => {
    if (status === "success") return "test-success";
    if (status === "failed") return "test-failed";
    return "";
  };

  const modelConnectivityLabel = (status) => {
    if (status === "success") return zhen("\u8fde\u901a\u6027\u5df2\u9a8c\u8bc1", "Connectivity Verified");
    if (status === "failed") return zhen("\u8fde\u901a\u6027\u9a8c\u8bc1\u5931\u8d25", "Connectivity Check Failed");
    return zhen("\u672a\u9a8c\u8bc1\u8fde\u901a\u6027", "Connectivity Not Verified");
  };

  const modelRoleLabel = (isActive) => (isActive
    ? zhen("\u5de5\u4f5c\u4e2d", "Active")
    : zhen("\u53ef\u5207\u6362", "Ready"));

  const modelDisplayValue = (value) => {
    if (value === null || value === undefined) return "-";
    const text = String(value).trim();
    return text || "-";
  };

  function createModelFacts(fields, extraClass = "") {
    const list = document.createElement("div");
    list.className = `model-facts${extraClass ? ` ${extraClass}` : ""}`;

    fields.forEach((field) => {
      const row = document.createElement("div");
      row.className = "model-fact";

      const label = document.createElement("span");
      label.className = "model-fact-label";
      label.textContent = field.label;

      const value = document.createElement("span");
      value.className = `model-fact-value${field.mono ? " mono" : ""}`;
      const displayValue = modelDisplayValue(field.value);
      value.textContent = displayValue;
      if (displayValue !== "-") value.title = displayValue;

      row.appendChild(label);
      row.appendChild(value);
      list.appendChild(row);
    });

    return list;
  }

  function renderModelRuntimeState(modelState, runtime) {
    refs.modelRuntimeState.innerHTML = "";
    if (!Object.keys(runtime || {}).length) {
      refs.modelRuntimeState.textContent = t("runtime_empty");
      return;
    }

    const summary = document.createElement("div");
    summary.className = "model-runtime-summary";

    const current = document.createElement("div");
    current.className = "model-runtime-current";

    const currentLabel = document.createElement("span");
    currentLabel.className = "model-runtime-current-label";
    currentLabel.textContent = zhen("\u5f53\u524d\u5de5\u4f5c\u6a21\u578b", "Active Model");

    const currentValue = document.createElement("strong");
    currentValue.className = "model-runtime-current-value";
    const activeProfileId = modelDisplayValue(modelState.active_profile_id);
    currentValue.textContent = activeProfileId;
    if (activeProfileId !== "-") currentValue.title = activeProfileId;

    current.appendChild(currentLabel);
    current.appendChild(currentValue);
    summary.appendChild(current);

    summary.appendChild(createModelFacts([
      { label: t("runtime_provider"), value: providerDisplayName(runtime.provider, runtime.provider || "-") },
      { label: t("runtime_model"), value: runtime.model },
      { label: t("runtime_base_url"), value: runtime.base_url, mono: true },
      { label: t("field_temperature"), value: runtime.temperature },
      { label: t("field_top_p"), value: runtime.top_p },
    ], "runtime-facts"));

    refs.modelRuntimeState.appendChild(summary);
  }

  function buildModelProfileCard(profile) {
    const card = document.createElement("article");
    card.className = `profile-card${profile.active ? " active" : ""}`;

    const status = profile.connectivity_status || "untested";
    const statusText = modelConnectivityLabel(status);
    const statusClass = connectivityClass(status);
    const statusTip = String(profile.connectivity_detail || "").trim() || statusText;

    const head = document.createElement("div");
    head.className = "profile-head";

    const titleGroup = document.createElement("div");
    titleGroup.className = "profile-title-group";

    const name = document.createElement("h4");
    name.className = "profile-name";
    const profileId = modelDisplayValue(profile.profile_id);
    name.textContent = profileId;
    if (profileId !== "-") name.title = profileId;

    const role = document.createElement("div");
    role.className = `profile-role${profile.active ? " active" : ""}`;
    role.textContent = modelRoleLabel(profile.active);

    titleGroup.appendChild(name);
    titleGroup.appendChild(role);

    const badge = document.createElement("span");
    badge.className = `profile-status${statusClass ? ` ${statusClass}` : ""}`;
    badge.textContent = statusText;
    badge.title = statusTip;

    head.appendChild(titleGroup);
    head.appendChild(badge);

    const facts = createModelFacts([
      { label: t("field_provider"), value: providerDisplayName(profile.provider, profile.provider || "-") },
      { label: t("field_model_name"), value: profile.model, mono: true },
      { label: t("field_base_url"), value: profile.base_url, mono: true },
      { label: t("field_api_key"), value: profile.api_key_masked, mono: true },
      { label: t("field_temperature"), value: profile.temperature },
      { label: t("field_top_p"), value: profile.top_p },
    ], "compact profile-details");

    const actions = document.createElement("div");
    actions.className = "profile-actions";

    const testBtn = document.createElement("button");
    testBtn.className = "btn-ghost profile-test-btn";
    testBtn.textContent = zhen("\u6d4b\u8bd5\u8fde\u901a\u6027", "Test Connectivity");
    testBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      testModelProfile(profile.profile_id).catch((err) => alert(`${t("action_failed")}: ${err}`));
    });

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "btn-ghost profile-delete-btn";
    deleteBtn.textContent = t("btn_delete");
    deleteBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      deleteModelProfile(profile.profile_id).catch((err) => alert(`${t("action_failed")}: ${err}`));
    });

    actions.appendChild(testBtn);
    actions.appendChild(deleteBtn);

    card.appendChild(head);
    card.appendChild(facts);
    card.appendChild(actions);

    card.addEventListener("click", () => activateModelProfile(profile.profile_id).catch((err) => alert(`${t("action_failed")}: ${err}`)));

    return card;
  }

  function renderModels() {
    const modelState = state.modelState || { providers: [], profiles: [], runtime: {} };
    const profiles = modelState.profiles || [];
    const runtime = modelState.runtime || {};

    renderModelProviderSelect(refs.modelProviderSelect.value);
    refreshModelModalText();
    renderModelRuntimeState(modelState, runtime);

    refs.modelProfilesGrid.innerHTML = "";
    if (!profiles.length) {
      refs.modelProfilesGrid.textContent = t("no_profiles");
      return;
    }

    const fragment = document.createDocumentFragment();
    profiles.forEach((profile) => {
      fragment.appendChild(buildModelProfileCard(profile));
    });
    refs.modelProfilesGrid.appendChild(fragment);
  }

  async function loadModels() {
    state.modelState = await api("/api/v1/models/state");
    renderModels();
  }

  function readModelPayload() {
    const profileId = refs.modelProfileIdInput.value.trim();
    if (!profileId) throw new Error("profile_id required");

    const provider = refs.modelProviderSelect.value.trim() || "openai";
    const preset = getProviderPreset(provider);
    const isCustom = Boolean(preset && preset.is_custom);

    const base = refs.modelBaseUrlInput.value.trim() || (isCustom ? "" : (preset && preset.default_base_url) || "");
    if (!base) throw new Error("base_url required");

    const modelName = refs.modelNameInput.value.trim() || (preset && preset.default_model) || "";
    if (!modelName) throw new Error("model required");
    const apiKey = refs.modelApiKeyInput.value.trim();
    if (!apiKey) throw new Error("api_key required");

    const temperature = parseOptionalNumber(refs.modelTemperatureInput.value, "temperature");
    const topP = parseOptionalNumber(refs.modelTopPInput.value, "top_p");
    if (topP != null && (topP <= 0 || topP > 1)) throw new Error("top_p must be > 0 and <= 1");

    return {
      profile_id: profileId,
      provider,
      base_url: base,
      model: modelName,
      api_key: apiKey,
      max_tokens: parseOptionalNumber(refs.modelMaxTokensInput.value, "max_tokens"),
      timeout: parseOptionalNumber(refs.modelTimeoutInput.value, "timeout"),
      temperature,
      top_p: topP,
      clear_api_key: false,
    };
  }

  async function saveModelProfile() {
    const payload = readModelPayload();
    state.modelState = await api("/api/v1/models/profiles", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    state.modelProfileId = payload.profile_id;
    closeModelModal();
    renderModels();
  }

  async function activateModelProfile(profileId) {
    const pid = (profileId || "").trim();
    if (!pid) throw new Error("profile_id required");
    state.modelState = await api("/api/v1/models/activate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile_id: pid }),
    });
    state.modelProfileId = pid;
    renderModels();
  }

  async function deleteModelProfile(profileId) {
    const pid = (profileId || "").trim();
    if (!pid) throw new Error("profile_id required");
    state.modelState = await api(`/api/v1/models/profiles/${encodeURIComponent(pid)}`, { method: "DELETE" });
    if (state.modelProfileId === pid) state.modelProfileId = "";
    renderModels();
  }

  async function testModelProfile(profileId) {
    const pid = (profileId || "").trim();
    if (!pid) throw new Error("profile_id required");
    state.modelState = await api(`/api/v1/models/profiles/${encodeURIComponent(pid)}/test`, { method: "POST" });
    renderModels();
  }

  function makeActionBtn(label, fn) {
    const btn = document.createElement("button");
    btn.className = "btn-ghost";
    btn.textContent = label;
    btn.addEventListener("click", async () => {
      try {
        await fn();
      } catch (err) {
        alert(`${t("action_failed")}: ${err}`);
      }
    });
    return btn;
  }

  function bindEvents() {
    refs.langToggleBtn.addEventListener("click", () => {
      state.lang = state.lang === "zh" ? "en" : "zh";
      localStorage.setItem(LANG_KEY, state.lang);
      document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
      applyI18n();
      renderSessions();
      renderMessages();
      renderEvents();
      renderChannels();
      renderCron();
      renderHeartbeat();
      renderSkills();
      renderModels();
      renderBillingStatus();
      renderBillingOverview();
      renderBillingCalls();
    });

    refs.navItems.forEach((btn) => {
      btn.addEventListener("click", async () => {
        const targetView = String(btn.dataset.view || "").trim();
        setView(targetView);
        try {
          await loadViewDataOnEnter(targetView);
        } catch (err) {
          alert(`${t("action_failed")}: ${err}`);
        }
      });
    });

    refs.sessionFilters.forEach((btn) => {
      btn.addEventListener("click", () => {
        state.filter = btn.dataset.filter;
        refs.sessionFilters.forEach((b) => b.classList.toggle("active", b === btn));
        renderSessions();
      });
    });

    refs.newSessionBtn.addEventListener("click", async () => {
      await api("/api/v1/sessions/new", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "web:local" }),
      });
      await loadSessions(false);
      const latest = state.sessions.find((s) => s.user_id === "web:local");
      if (latest) await selectSession(latest);
    });

    refs.refreshSessionsBtn.addEventListener("click", () => loadSessions(false));
    refs.sendBtn.addEventListener("click", () => sendMessage().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    if (refs.voiceInputBtn) refs.voiceInputBtn.addEventListener("click", () => toggleVoiceInput());
    refs.chatInput.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") sendMessage().catch((err) => alert(`${t("action_failed")}: ${err}`));
    });
    refs.cancelBtn.addEventListener("click", () => cancelCurrent().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    refs.fileInput.addEventListener("change", async (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      try {
        await uploadFile(file);
      } catch (err) {
        alert(`${t("upload_failed")}: ${err}`);
      } finally {
        refs.fileInput.value = "";
      }
    });

    refs.reloadCronBtn.addEventListener("click", () => loadCron().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    if (refs.reloadChannelsBtn) refs.reloadChannelsBtn.addEventListener("click", () => loadChannels().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    if (refs.saveChannelBtn) refs.saveChannelBtn.addEventListener("click", () => saveChannelConfig().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    if (refs.cancelChannelBtn) refs.cancelChannelBtn.addEventListener("click", () => closeChannelDrawer());
    if (refs.closeChannelDrawerBtn) refs.closeChannelDrawerBtn.addEventListener("click", () => closeChannelDrawer());
    if (refs.channelDrawer) {
      refs.channelDrawer.addEventListener("click", (event) => {
        if (event.target === refs.channelDrawer) closeChannelDrawer();
      });
    }
    refs.createCronBtn.addEventListener("click", () => createCron().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    refs.reloadHeartbeatBtn.addEventListener("click", () => loadHeartbeat().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    refs.saveHeartbeatBtn.addEventListener("click", () => saveHeartbeat().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    refs.runHeartbeatBtn.addEventListener("click", () => runHeartbeat().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    refs.reloadSkillsBtn.addEventListener("click", () => loadSkills().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    refs.reloadModelsBtn.addEventListener("click", () => loadModels().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    refs.newModelBtn.addEventListener("click", () => openModelModal());
    refs.closeModelModalBtn.addEventListener("click", () => closeModelModal());
    refs.cancelModelModalBtn.addEventListener("click", () => closeModelModal());
    refs.saveModelProfileBtn.addEventListener("click", () => saveModelProfile().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    refs.modelProviderSelect.addEventListener("change", () => applyProviderPreset(refs.modelProviderSelect.value, true));
    refs.modelModal.addEventListener("click", (event) => {
      if (event.target === refs.modelModal) closeModelModal();
    });
    if (refs.runSearchBtn) refs.runSearchBtn.addEventListener("click", () => runSearch().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    if (refs.reindexSearchBtn) refs.reindexSearchBtn.addEventListener("click", () => reindexSearch().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    if (refs.refreshSearchStatusBtn) refs.refreshSearchStatusBtn.addEventListener("click", () => loadSearchStatus().catch((err) => alert(`${t("action_failed")}: ${err}`)));
    if (refs.searchInput) {
      refs.searchInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") runSearch().catch((err) => alert(`${t("action_failed")}: ${err}`));
      });
    }
    if (refs.refreshBillingBtn) refs.refreshBillingBtn.addEventListener("click", () => reloadBilling(false).catch((err) => alert(`${t("action_failed")}: ${err}`)));
    if (refs.applyBillingFiltersBtn) refs.applyBillingFiltersBtn.addEventListener("click", () => reloadBilling(true).catch((err) => alert(`${t("action_failed")}: ${err}`)));
    if (refs.billingQuickRange) {
      refs.billingQuickRange.addEventListener("change", () => {
        applyBillingQuickRange(refs.billingQuickRange.value);
        reloadBilling(true).catch((err) => alert(`${t("action_failed")}: ${err}`));
      });
    }
    if (refs.billingPrevBtn) {
      refs.billingPrevBtn.addEventListener("click", () => {
        const totalPages = Math.max(1, Math.ceil((state.billingTotal || 0) / 20));
        state.billingPage = Math.max(1, Math.min(totalPages, (state.billingPage || 1) - 1));
        loadBillingCalls().catch((err) => alert(`${t("action_failed")}: ${err}`));
      });
    }
    if (refs.billingNextBtn) {
      refs.billingNextBtn.addEventListener("click", () => {
        const totalPages = Math.max(1, Math.ceil((state.billingTotal || 0) / 20));
        state.billingPage = Math.max(1, Math.min(totalPages, (state.billingPage || 1) + 1));
        loadBillingCalls().catch((err) => alert(`${t("action_failed")}: ${err}`));
      });
    }
    if (refs.closeBillingDetailBtn) refs.closeBillingDetailBtn.addEventListener("click", () => closeBillingDetail());
    if (refs.billingDetailModal) {
      refs.billingDetailModal.addEventListener("click", (event) => {
        if (event.target === refs.billingDetailModal) closeBillingDetail();
      });
    }
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && refs.channelDrawer && !refs.channelDrawer.classList.contains("hidden")) {
        closeChannelDrawer();
        return;
      }
      if (event.key === "Escape" && refs.billingDetailModal && !refs.billingDetailModal.classList.contains("hidden")) {
        closeBillingDetail();
        return;
      }
      if (event.key === "Escape" && !refs.modelModal.classList.contains("hidden")) {
        closeModelModal();
      }
    });
    window.addEventListener("beforeunload", () => {
      stopBillingAutoRefresh();
      stopSessionAutoRefresh();
      try {
        stopVoiceInput();
      } catch {
        // Ignore cleanup failures.
      }
      cleanupVoiceStream();
    });
  }

  async function refreshSelectedSessionMessages(force = false) {
    if (!state.selected) return false;
    const userId = String(state.selected.user_id || "");
    const sessionName = String(state.selected.session_name || "");
    if (!userId || !sessionName) return false;

    const qs = new URLSearchParams({ user_id: userId, session_name: sessionName });
    const data = await api(`/api/v1/sessions/messages?${qs.toString()}`);
    const preferredRows = Array.isArray(data.render_messages) ? data.render_messages : [];
    const fallbackRows = Array.isArray(data.messages) ? data.messages : [];
    let normalized = normalizeMessages(preferredRows.length ? preferredRows : fallbackRows);
    if (!normalized.length && fallbackRows.length && preferredRows !== fallbackRows) {
      normalized = normalizeMessages(fallbackRows);
    }

    const sig = buildMessageSignature(normalized);
    if (!force && sig === state.selectedSessionMsgSig) return false;
    state.selectedSessionMsgSig = sig;
    state.messages = normalized;
    renderMessages();
    return true;
  }

  function stopSessionAutoRefresh() {
    if (state.sessionAutoRefreshTimer) {
      clearInterval(state.sessionAutoRefreshTimer);
      state.sessionAutoRefreshTimer = null;
    }
  }

  function startSessionAutoRefresh() {
    stopSessionAutoRefresh();
    if (state.view !== "chat") return;
    state.sessionAutoRefreshTimer = setInterval(() => {
      if (state.view !== "chat") return;
      if (!state.selected) return;
      // Avoid overriding streaming UI while an active request is running.
      if (state.currentRequestId) return;
      refreshSelectedSessionMessages(false).catch((err) => {
        console.warn("session auto refresh failed", err);
      });
    }, Number(state.sessionAutoRefreshMs || 1500));
  }

  async function boot() {
    bindEvents();
    document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
    applyI18n();
    await loadHealth();
    await loadSessions();
    await loadChannels();
    await loadCron();
    await loadHeartbeat();
    await loadSkills();
    await loadModels();
    await loadSearchStatus();
    if (refs.billingQuickRange) refs.billingQuickRange.value = "12h";
    applyBillingQuickRange("12h");
    readBillingFilters(true);
    await loadBillingStatus();
    updateVoiceUi();
    setView("chat");
  }

  boot().catch((err) => {
    console.error(err);
    alert(`${t("init_failed")}: ${err}`);
  });
})();
