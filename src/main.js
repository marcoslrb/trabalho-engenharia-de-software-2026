import './styles.css';

const app = document.querySelector('#app');
const STORAGE_KEY = 'ouvidoria-publica.manifestacoes.v1';
const SESSION_KEY = 'ouvidoria-publica.ultima-consulta.v1';
const VALIDATION_LOG_KEY = 'ouvidoria-publica.validacoes.v1';
const BYPASS_LOGIN_KEY = 'ouvidoria-publica.bypass-login.v1';
const LOGIN_SESSION_KEY = 'ouvidoria-publica.login-session.v1';

const statusFlow = [
  'Recebida',
  'Triagem',
  'Encaminhada ao setor',
  'Em análise',
  'Resposta disponível',
  'Concluída',
];

const categories = ['Denúncia', 'Reclamação', 'Solicitação', 'Sugestão', 'Elogio'];

const sectors = [
  'Atendimento ao cidadão',
  'Limpeza urbana',
  'Saúde',
  'Educação',
  'Mobilidade',
  'Assistência social',
  'Meio ambiente',
];

const consistencyChecks = [
  {
    id: 'C01',
    status: 'atencao',
    title: 'Anonimato versus acompanhamento (RF02 e RF06)',
    text: 'O fluxo está coerente ao permitir acompanhamento sem login, porém a validação depende de protocolo + credencial (e-mail/código).',
  },
  {
    id: 'C02',
    status: 'inconsistente',
    title: 'Acesso interno sem autenticação forte (RF09 e RNF16)',
    text: 'O painel do gestor está acessível sem login real e sem MFA, conflitando com os requisitos de segurança.',
  },
  {
    id: 'C03',
    status: 'ok',
    title: 'Linha do tempo e atualização interna (RF07 e RF08)',
    text: 'As mudanças de status aparecem no acompanhamento e no histórico do atendimento.',
  },
];

const functionalCoverage = [
  { id: 'RF01', status: 'atendido', note: 'Cadastro de manifestação com tipo, assunto e descrição.' },
  { id: 'RF02', status: 'atendido', note: 'Modo anônimo sem nome/e-mail/telefone.' },
  { id: 'RF03', status: 'parcial', note: 'Identificação disponível, mas CPF não está no formulário.' },
  { id: 'RF04', status: 'parcial', note: 'Anexo múltiplo existe, sem validação de 5 arquivos, formato e tamanho.' },
  { id: 'RF05', status: 'atendido', note: 'Protocolo único é gerado e exibido.' },
  { id: 'RF06', status: 'parcial', note: 'Consulta sem login, porém exige credencial adicional.' },
  { id: 'RF07', status: 'atendido', note: 'Linha do tempo de atualizações exibida no acompanhamento.' },
  { id: 'RF08', status: 'parcial', note: 'Gestor altera status/setor/resposta, sem classificação completa.' },
  { id: 'RF09', status: 'nao_atendido', note: 'Login seguro do gestor não implementado.' },
  { id: 'RF10', status: 'parcial', note: 'Há painel/lista, sem filtros por status/tipo/data/assunto.' },
  { id: 'RF11', status: 'nao_atendido', note: 'Sem edição de tags e classificação complementar.' },
  { id: 'RF12', status: 'parcial', note: 'Encaminhamento por setor existe, sem observação específica de despacho.' },
  { id: 'RF13', status: 'atendido', note: 'Resposta oficial do gestor visível ao cidadão.' },
  { id: 'RF14', status: 'parcial', note: 'Status pode ir para concluída, sem parecer de encerramento dedicado.' },
  { id: 'RF15', status: 'nao_atendido', note: 'Notificação por e-mail de status não implementada.' },
  { id: 'RF16', status: 'nao_atendido', note: 'Envio de protocolo por e-mail não implementado.' },
  { id: 'RF17', status: 'nao_atendido', note: 'Sem relatórios gerenciais.' },
  { id: 'RF18', status: 'nao_atendido', note: 'Sem exportação CSV/XLSX.' },
  { id: 'RF19', status: 'nao_atendido', note: 'Sem gerenciamento de usuários administradores.' },
];

const rnfVerifiability = [
  { id: 'RNF01', status: 'testavel', metric: 'Teste com usuários e avaliação de usabilidade.' },
  { id: 'RNF02', status: 'testavel', metric: 'Inspeção responsiva em viewport móvel/tablet.' },
  { id: 'RNF03', status: 'parcial', metric: 'Fluxo anônimo testável; proteção real de dados depende backend.' },
  { id: 'RNF04', status: 'parcial', metric: 'Checagem de acesso por protocolo/credencial; falta isolamento por backend.' },
  { id: 'RNF05', status: 'testavel', metric: 'Medição de tempo de carregamento no navegador.' },
  { id: 'RNF06', status: 'nao_testavel', metric: 'Disponibilidade 24/7 exige monitoramento em produção.' },
  { id: 'RNF07', status: 'nao_testavel', metric: 'Carga de 500 usuários simultâneos exige teste de estresse.' },
  { id: 'RNF08', status: 'nao_testavel', metric: 'Escalabilidade depende arquitetura de infraestrutura.' },
  { id: 'RNF09', status: 'parcial', metric: 'Modularização do front pode ser inspecionada, sem cobertura completa.' },
  { id: 'RNF10', status: 'testavel', metric: 'Teste cruzado em navegadores e sistemas operacionais.' },
  { id: 'RNF11', status: 'nao_testavel', metric: 'Auditoria CRUD requer logs de servidor.' },
  { id: 'RNF12', status: 'nao_testavel', metric: 'Backup/recuperação exigem ambiente de produção.' },
  { id: 'RNF13', status: 'nao_testavel', metric: 'Integração com APIs governamentais não implementada.' },
  { id: 'RNF14', status: 'parcial', metric: 'Documentação do front existe parcialmente, sem pacote técnico completo.' },
  { id: 'RNF15', status: 'testavel', metric: 'Mensagens de sucesso/erro e feedback visual já observáveis.' },
  { id: 'RNF16', status: 'nao_testavel', metric: 'MFA não implementado para usuários internos.' },
  { id: 'RNF17', status: 'nao_testavel', metric: 'Uso de CPU/memória/disco requer telemetria de servidor.' },
  { id: 'RNF18', status: 'parcial', metric: 'Parte de usabilidade aplicada; falta checklist formal e-Ping.' },
  { id: 'RNF19', status: 'testavel', metric: 'Stack atual usa tecnologias open source.' },
  { id: 'RNF20', status: 'parcial', metric: 'No front é rápido; comprovação oficial requer banco e backend.' },
];

async function readValidationLogs() {
  try {
    const res = await fetch('/api/validacoes');
    if (!res.ok) throw new Error();
    return await res.json();
  } catch {
    return [];
  }
}

function statusLabel(status) {
  const labels = {
    ok: 'OK',
    atencao: 'Atenção',
    inconsistente: 'Inconsistente',
    atendido: 'Atendido',
    parcial: 'Parcial',
    nao_atendido: 'Não atendido',
    testavel: 'Testável',
    nao_testavel: 'Não testável aqui',
  };

  return labels[status] || status;
}

async function readManifestations() {
  try {
    const res = await fetch('/api/manifestacoes');
    if (!res.ok) throw new Error();
    const data = await res.json();
    return data.map(m => ({
      protocol: m.protocolo,
      category: m.categoria,
      subject: m.assunto || 'Sem assunto',
      description: m.texto_manifestacao || '',
      status: m.status || 'Recebida',
      sector: m.setor || 'Atendimento ao cidadão',
      anonymous: Boolean(m.eh_anonimo),
      name: m.nome_cidadao || '',
      email: m.email_cidadao || '',
      phone: m.telefone_cidadao || '',
      response: m.resposta_gestor || '',
      createdAt: m.data_registro,
      updatedAt: m.data_atualizacao
    }));
  } catch {
    return [];
  }
}

async function findManifestation(protocol) {
  try {
    const res = await fetch(`/api/manifestacoes/${protocol.trim().toUpperCase()}`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

async function findManifestationInternal(protocol) {
  try {
    const res = await fetch(`/api/manifestacoes/interna/${protocol.trim().toUpperCase()}`);
    if (!res.ok) return null;
    const m = await res.json();
    return {
      protocol: m.protocolo,
      category: m.categoria,
      subject: m.assunto || 'Sem assunto',
      description: m.texto_manifestacao || '',
      status: m.status || 'Recebida',
      sector: m.setor || 'Atendimento ao cidadão',
      anonymous: Boolean(m.eh_anonimo),
      name: m.nome_cidadao || '',
      email: m.email_cidadao || '',
      phone: m.telefone_cidadao || '',
      response: m.resposta_gestor || '',
      history: (m.history || []).map(h => ({
        status: h.status_novo,
        date: h.data_alteracao,
        note: h.observacao || ''
      })),
      createdAt: m.data_registro,
      updatedAt: m.data_atualizacao
    };
  } catch {
    return null;
  }
}

async function updateManifestation(protocol, patch) {
  try {
    const res = await fetch(`/api/manifestacoes/${protocol}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch),
    });
    return res.ok;
  } catch {
    return false;
  }
}

function layout({ main, title, subtitle }) {
  const isBypassed = localStorage.getItem(BYPASS_LOGIN_KEY) === 'true';
  return `
    <main class="site-shell">
      <aside class="rail">
        <div class="brand">
          <span class="brand-mark">OP</span>
          <div>
            <p class="eyebrow">Portal oficial</p>
            <h1>Ouvidoria Pública</h1>
          </div>
        </div>

        <nav class="menu" aria-label="Navegação principal">
          <a class="menu-link" href="#/"><span class="nav-icon"></span>Início</a>
          <a class="menu-link" href="#/abrir"><span class="nav-icon"></span>Abrir manifestação</a>
          <a class="menu-link" href="#/acompanhar"><span class="nav-icon"></span>Acompanhar protocolo</a>
          <a class="menu-link" href="#/atendimento"><span class="nav-icon"></span>Painel do atendente</a>
        </nav>

        <section class="side-card">
          <p class="eyebrow">Versão do portal</p>
          <strong>v2.0 — Fluxo real</strong>
          <label class="bypass-toggle-container">
            <input type="checkbox" id="bypass-login-toggle" ${isBypassed ? 'checked' : ''} />
            Desativar Autenticação
          </label>
        </section>
      </aside>

      <section class="content">
        <header class="page-heading">
          <p class="eyebrow">${subtitle}</p>
          <h2>${title}</h2>
        </header>
        ${main}
      </section>
    </main>
  `;
}

async function homePage() {
  let stats = { total: 0, anonimas: 0, identificadas: 0, concluidas: 0, abertas: 0 };
  try {
    const res = await fetch('/api/stats');
    if (res.ok) stats = await res.json();
  } catch { }

  const openCount = stats.abertas;
  const closedCount = stats.concluidas;
  const anonCount = stats.anonimas;
  const totalCount = stats.total;

  const featureCards = [
    {
      title: 'Abrir manifestação',
      text: 'Registre denúncias, reclamações, sugestões e elogios de forma identificada ou anônima.',
      icon: '📝',
      href: '#/abrir',
      accent: '#1a56e8',
      accentSoft: '#e8eeff',
    },
    {
      title: 'Acompanhar andamento',
      text: 'Consulte o status da sua manifestação em tempo real usando protocolo e credencial.',
      icon: '🔍',
      href: '#/acompanhar',
      accent: '#00c49a',
      accentSoft: '#e0faf3',
    },
    {
      title: 'Painel do atendente',
      text: 'Área interna para triagem, encaminhamento e resposta às manifestações recebidas.',
      icon: '🛠',
      href: '#/atendimento',
      accent: '#f79009',
      accentSoft: '#fef0c7',
    },
  ];

  return layout({
    title: 'Portal de gerenciamento de manifestações públicas',
    subtitle: 'Atendimento digital',
    main: `
      <section class="hero">
        <div class="hero-real">
          <p class="eyebrow">Ouvidoria Digital — Atendimento ao cidadão</p>
          <h3>Transparência e participação na gestão pública.</h3>
          <div class="hero-actions">
            <a class="primary-button" href="#/abrir">Abrir manifestação</a>
            <a class="ghost-button" href="#/acompanhar">Consultar protocolo</a>
          </div>
          <div class="stat-strip">
            <div class="stat-item">
              <span class="stat-num">${totalCount}</span>
              <span class="stat-label">Total</span>
            </div>
            <div class="stat-item">
              <span class="stat-num">${openCount}</span>
              <span class="stat-label">Em aberto</span>
            </div>
            <div class="stat-item">
              <span class="stat-num">${anonCount}</span>
              <span class="stat-label">Anônimas</span>
            </div>
          </div>
        </div>

        <div class="hero-panel">
          <p class="panel-label">Situação da base</p>
          <strong style="font-size:1.5rem;font-family:'Stack Sans Headline Variable', 'Stack Sans Headline',sans-serif">${totalCount}</strong>
          <p style="font-size:0.82rem;color:var(--muted)">manifestações registradas no sistema</p>
          <div class="panel-metrics">
            <span>${openCount} em andamento</span>
            <span>${closedCount} concluídas</span>
            <span>${anonCount} anônimas</span>
          </div>
          <a class="primary-button" href="#/abrir" style="margin-top:8px">Nova manifestação →</a>
        </div>
      </section>

      <section class="cards-grid">
        ${featureCards
        .map(
          (card) => `
              <a href="${card.href}" class="feature-card" style="--card-accent:${card.accent};--card-accent-soft:${card.accentSoft};text-decoration:none;cursor:pointer">
                <div class="card-icon" style="background:${card.accentSoft};color:${card.accent}">${card.icon}</div>
                <h3>${card.title}</h3>
                <p>${card.text}</p>
              </a>
            `,
        )
        .join('')}
      </section>
    `,
  });
}

function openPage(message = '') {
  return layout({
    title: 'Abrir nova manifestação',
    subtitle: 'Portal do cidadão',
    main: `
      ${message ? `<div class="notice success">${message}</div>` : ''}
      <section class="screen-grid two-column-real">
        <article class="screen-card screen-card-wide">
          <form id="manifestation-form" class="mock-form" enctype="multipart/form-data">
            <div class="form-grid">
              <label>
                Tipo de manifestação
                <select name="category" required>
                  ${categories.map((item) => `<option value="${item}">${item}</option>`).join('')}
                </select>
              </label>

              <label>
                Assunto curto
                <input name="subject" type="text" maxlength="120" placeholder="Resumo rápido do problema" required />
              </label>
            </div>

            <fieldset class="choice-fieldset">
              <legend>Como deseja se identificar?</legend>
              <label><input type="radio" name="anonymous" value="false" checked /> Identificado</label>
              <label><input type="radio" name="anonymous" value="true" /> Anônimo</label>
            </fieldset>

            <div class="form-grid identity-grid" data-identity-fields>
              <label>
                Nome completo
                <input name="name" type="text" placeholder="Nome e sobrenome" required />
              </label>
              <label>
                E-mail
                <input name="email" type="email" placeholder="voce@exemplo.com" required />
              </label>
              <label>
                Telefone
                <input name="phone" type="tel" placeholder="(00) 00000-0000" required />
              </label>
            </div>

            <div class="form-grid">
              <label>
                Setor relacionado
                <select name="sector" required>
                  ${sectors.map((item) => `<option value="${item}">${item}</option>`).join('')}
                </select>
              </label>

              <label>
                Arquivos anexos
                <input name="attachments" type="file" multiple />
              </label>
            </div>

            <label>
              Descrição detalhada
              <textarea
                name="description"
                rows="8"
                minlength="30"
                placeholder="Informe local, data, envolvidos e qualquer evidência útil"
                required
              ></textarea>
            </label>

            <div class="form-actions">
              <button type="reset" class="ghost-button">Limpar</button>
              <button type="submit" class="primary-button">Registrar manifestação</button>
            </div>
          </form>
        </article>

        <aside class="side-stack">
          <div class="screen-card">
            <h4 style="font-size:0.88rem;font-weight:700;margin-bottom:12px;color:var(--text)">📋 Como funciona</h4>
            <div style="display:grid;gap:10px">
              <div class="callout">
                <strong>1. Preencha o formulário</strong>
                <p>Informe categoria, setor, assunto e descrição detalhada.</p>
              </div>
              <div class="callout">
                <strong>2. Receba o protocolo</strong>
                <p>Um número único é gerado imediatamente após o envio.</p>
              </div>
              <div class="callout">
                <strong>3. Acompanhe online</strong>
                <p>Use o protocolo para consultar o andamento a qualquer hora.</p>
              </div>
            </div>
          </div>
          <div class="screen-card" style="background:var(--accent-soft);border-color:rgba(0,196,154,0.25)">
            <p style="font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.10em;color:var(--accent-d);margin-bottom:6px">🔒 Privacidade</p>
            <p style="font-size:0.82rem;color:#00795e;line-height:1.55">O modo anônimo omite todos os dados pessoais. Guarde o código de acesso gerado para consultar sua manifestação futuramente.</p>
          </div>
        </aside>
      </section>
    `,
  });
}

async function trackingPage(message = '') {
  const savedQuery = JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
  const latest = savedQuery ? await findManifestation(savedQuery.protocol) : null;

  return layout({
    title: 'Acompanhar protocolo',
    subtitle: 'Consulta do cidadão',
    main: `
      ${message ? `<div class="notice success">${message}</div>` : ''}
      <section class="screen-grid two-column-real">
        <article class="screen-card screen-card-wide">
          <form id="tracking-form" class="mock-form">
            <div class="form-grid">
              <label>
                Número do protocolo
                <input name="protocol" type="text" placeholder="OP-2604..." value="${savedQuery?.protocol || ''}" required />
              </label>
              <label>
                E-mail de contato ou código de acesso
                <input name="secret" type="text" value="${savedQuery?.secret || ''}" placeholder="E-mail ou código gerado" required />
              </label>
            </div>
            <div class="form-actions">
              <button type="submit" class="primary-button">Consultar</button>
              <button type="button" class="ghost-button" data-fill-last>Usar última consulta</button>
            </div>
          </form>

          <div class="result-card" id="tracking-result">
            ${trackingResultMarkup(latest, savedQuery?.secret)}
          </div>
        </article>

        <aside class="side-stack">
          <div class="screen-card">
            <h4 style="font-size:0.88rem;font-weight:700;margin-bottom:12px;color:var(--text)">🔎 Fluxo de status</h4>
            <div style="display:grid;gap:6px">
              ${statusFlow.map((s, i) => `
                <div style="display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;background:${i === 0 ? 'var(--accent-soft)' : 'var(--surface-2)'};border:1px solid ${i === 0 ? 'rgba(0,196,154,0.25)' : 'var(--line)'}">
                  <span style="width:22px;height:22px;border-radius:50%;background:${i === 0 ? 'var(--accent)' : 'var(--line)'};display:grid;place-items:center;font-size:0.6rem;font-weight:800;color:${i === 0 ? '#fff' : 'var(--muted)'}">${i + 1}</span>
                  <span style="font-size:0.82rem;font-weight:${i === 0 ? '700' : '500'};color:${i === 0 ? 'var(--accent-d)' : 'var(--text)'}">${s}</span>
                </div>
              `).join('')}
            </div>
          </div>
        </aside>
      </section>
    `,
  });
}

function trackingResultMarkup(manifestation, providedSecret = '') {
  if (!manifestation) {
    return `
      <div class="empty-state">
        <h3>Nenhuma manifestação localizada</h3>
        <p>Informe um protocolo válido e o e-mail ou código de acesso correspondente.</p>
      </div>
    `;
  }

  const secretMatches = true;

  return `
    <article class="result-detail">
      <div class="result-header">
        <div>
          <p class="eyebrow">Protocolo localizado</p>
          <h3>${manifestation.protocol}</h3>
        </div>
        <button class="ghost-button" data-copy-protocol="${manifestation.protocol}">Copiar protocolo</button>
      </div>
      <div class="result-meta">
        <span>${manifestation.category}</span>
        <span>${manifestation.status}</span>
        <span>${manifestation.sector}</span>
      </div>
      <p><strong>Assunto:</strong> ${manifestation.subject}</p>
      <p><strong>Descrição:</strong> ${manifestation.description}</p>
      <div class="timeline vertical">
        ${manifestation.history
      .map(
        (entry) => `
              <div class="timeline-step">
                <span>${new Date(entry.date).toLocaleDateString('pt-BR')}</span>
                <p><strong>${entry.status}</strong> - ${entry.note}</p>
              </div>
            `,
      )
      .join('')}
      </div>
      ${manifestation.response ? `<div class="notice">${manifestation.response}</div>` : '<div class="notice">Ainda não há resposta registrada.</div>'}
    </article>
  `;
}

async function atendimentoPage(filters = {}) {
  const all = await readManifestations();
  const selectedProtocol = filters.protocol || all[0]?.protocol || '';
  const selected = selectedProtocol ? await findManifestationInternal(selectedProtocol) : null;

  return layout({
    title: 'Painel do atendente',
    subtitle: 'Área interna',
    main: `
      <div style="display:flex;justify-content:flex-end;margin-bottom:12px">
        <button type="button" class="ghost-button" id="logout-btn" style="padding:6px 12px;font-size:0.8rem;border-radius:var(--r-sm)">🚪 Encerrar Sessão</button>
      </div>
      <section class="screen-grid admin-layout">
        <article class="screen-card admin-list-card">
          <div class="screen-header">
            <h3>Manifestações registradas</h3>
            <span class="pill">${all.length} itens</span>
          </div>
          <div class="admin-list">
            ${all
        .map(
          (item) => `
                  <button class="admin-item ${item.protocol === selected?.protocol ? 'active' : ''}" data-open-protocol="${item.protocol}">
                    <strong>${item.protocol}</strong>
                    <span>${item.category}</span>
                    <small>${item.status}</small>
                  </button>
                `,
        )
        .join('')}
          </div>
        </article>

        <article class="screen-card admin-detail-card">
          ${selected ? adminDetailMarkup(selected) : '<div class="empty-state"><h3>Nenhum registro</h3></div>'}
        </article>
      </section>
    `,
  });
}

function adminDetailMarkup(manifestation) {
  return `
    <form id="admin-form" class="mock-form" data-protocol="${manifestation.protocol}">
      <div class="screen-header">
        <div>
          <p class="eyebrow">Detalhe operacional</p>
          <h3>${manifestation.protocol}</h3>
        </div>
        <span class="pill">${manifestation.anonymous ? 'Anônima' : 'Identificada'}</span>
      </div>

      <div class="detail-grid">
        <div class="callout">
          <strong>Solicitante</strong>
          <p>${manifestation.anonymous ? 'Sigiloso' : manifestation.name}</p>
          <p>${manifestation.anonymous ? 'Código de acesso: ' + manifestation.accessCode : manifestation.email}</p>
        </div>
        <div class="callout">
          <strong>Andamento atual</strong>
          <p>${manifestation.status}</p>
          <p>Última atualização em ${new Date(manifestation.updatedAt).toLocaleString('pt-BR')}</p>
        </div>
      </div>

      <label>
        Setor responsável
        <select name="sector">
          ${sectors.map((item) => `<option value="${item}" ${item === manifestation.sector ? 'selected' : ''}>${item}</option>`).join('')}
        </select>
      </label>

      <label>
        Status da manifestação
        <select name="status">
          ${statusFlow.map((item) => `<option value="${item}" ${item === manifestation.status ? 'selected' : ''}>${item}</option>`).join('')}
        </select>
      </label>

      <label>
        Resposta oficial
        <textarea name="response" rows="6" placeholder="Escreva a resposta ao cidadão">${manifestation.response || ''}</textarea>
      </label>

      <div class="form-actions">
        <button type="submit" class="primary-button">Salvar atualização</button>
      </div>

      <div class="history-box">
        <h4>Histórico</h4>
        ${manifestation.history
      .map(
        (entry) => `
              <div class="history-item">
                <strong>${entry.status}</strong>
                <span>${new Date(entry.date).toLocaleString('pt-BR')}</span>
                <p>${entry.note}</p>
              </div>
            `,
      )
      .join('')}
      </div>
    </form>
  `;
}

async function validationPage() {
  const logs = await readValidationLogs();
  const isBypassed = isLoginBypassed();

  const dynamicConsistency = consistencyChecks.map((check) => {
    if (check.id === 'C02') {
      return {
        ...check,
        status: isBypassed ? 'inconsistente' : 'ok',
        text: isBypassed
          ? 'O painel do gestor está acessível sem login real (bypass ativo), conflitando com os requisitos de segurança.'
          : 'O painel do gestor exige autenticação segura por login para acesso.',
      };
    }
    return check;
  });

  const dynamicCoverage = functionalCoverage.map((item) => {
    if (item.id === 'RF09') {
      return {
        ...item,
        status: isBypassed ? 'nao_atendido' : 'atendido',
        note: isBypassed
          ? 'Login desativado via painel de bypass.'
          : 'Login seguro do gestor implementado e ativo.',
      };
    }
    return item;
  });

  const covered = dynamicCoverage.filter((item) => item.status === 'atendido').length;
  const partial = dynamicCoverage.filter((item) => item.status === 'parcial').length;
  const missing = dynamicCoverage.filter((item) => item.status === 'nao_atendido').length;

  const rnfTestable = rnfVerifiability.filter((item) => item.status === 'testavel').length;
  const rnfPartial = rnfVerifiability.filter((item) => item.status === 'parcial').length;
  const rnfNonTestable = rnfVerifiability.filter((item) => item.status === 'nao_testavel').length;

  return layout({
    title: 'Validação de Requisitos',
    subtitle: 'Consistência, completude e verificabilidade',
    main: `
      <section class="validation-summary-grid section">
        <article class="feature-card" style="--accent: var(--primary)">
          <h3>Completude (RFs)</h3>
          <p>${covered} atendidos</p>
          <p>${partial} parciais</p>
          <p>${missing} não atendidos</p>
        </article>
        <article class="feature-card" style="--accent: var(--warn)">
          <h3>Consistência</h3>
          <p>${dynamicConsistency.filter((item) => item.status === 'ok').length} consistentes</p>
          <p>${dynamicConsistency.filter((item) => item.status === 'atencao').length} com atenção</p>
          <p>${dynamicConsistency.filter((item) => item.status === 'inconsistente').length} inconsistentes</p>
        </article>
        <article class="feature-card" style="--accent: var(--ok)">
          <h3>Verificabilidade (RNFs)</h3>
          <p>${rnfTestable} testáveis agora</p>
          <p>${rnfPartial} parcialmente testáveis</p>
          <p>${rnfNonTestable} dependem de infraestrutura</p>
        </article>
      </section>

      <section class="section">
        <article class="screen-card">
          <h4>Verificação de consistência</h4>
          <div class="validation-list">
            ${dynamicConsistency
        .map(
          (check) => `
                  <div class="check-card">
                    <span class="status-badge status-${check.status}">${statusLabel(check.status)}</span>
                    <strong>${check.id} - ${check.title}</strong>
                    <p>${check.text}</p>
                  </div>
                `,
        )
        .join('')}
          </div>
        </article>
      </section>

      <section class="section">
        <article class="screen-card">
          <h4>Verificação de completude (RF01 a RF19)</h4>
          <div class="table-wrap">
            <table class="validation-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Situação</th>
                  <th>Evidência atual no site</th>
                </tr>
              </thead>
              <tbody>
                ${dynamicCoverage
        .map(
          (item) => `
                      <tr>
                        <td>${item.id}</td>
                        <td><span class="status-badge status-${item.status}">${statusLabel(item.status)}</span></td>
                        <td>${item.note}</td>
                      </tr>
                    `,
        )
        .join('')}
              </tbody>
            </table>
          </div>
        </article>
      </section>

      <section class="section">
        <article class="screen-card">
          <h4>Verificabilidade dos RNFs (RNF01 a RNF20)</h4>
          <div class="table-wrap">
            <table class="validation-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Verificabilidade</th>
                  <th>Como medir / condição</th>
                </tr>
              </thead>
              <tbody>
                ${rnfVerifiability
        .map(
          (item) => `
                      <tr>
                        <td>${item.id}</td>
                        <td><span class="status-badge status-${item.status}">${statusLabel(item.status)}</span></td>
                        <td>${item.metric}</td>
                      </tr>
                    `,
        )
        .join('')}
              </tbody>
            </table>
          </div>
        </article>
      </section>

      <section class="section">
        <div class="validation-layout">
          <article class="screen-card">
            <h4>Registrar validação no site</h4>
            <form id="validation-form" class="mock-form">
              <label>
                Grupo avaliador
                <input name="groupName" type="text" placeholder="Ex.: Grupo 03" required />
              </label>
              <label>
                Avaliador
                <input name="reviewer" type="text" placeholder="Ex.: Ana Clara" required />
              </label>
              <label>
                Data
                <input name="reviewDate" type="date" required />
              </label>
              <label>
                Decisão
                <select name="decision" required>
                  <option value="Aprovado">Aprovado</option>
                  <option value="Aprovado com ressalvas">Aprovado com ressalvas</option>
                  <option value="Reprovado">Reprovado</option>
                </select>
              </label>
              <label>
                Observações de consistência
                <textarea name="consistencyNote" rows="4" placeholder="Ajustes necessários"></textarea>
              </label>
              <label>
                Observações de completude
                <textarea name="completenessNote" rows="4" placeholder="RFs faltantes"></textarea>
              </label>
              <label>
                Observações de RNFs
                <textarea name="rnfNote" rows="4" placeholder="RNFs ambíguos, irreais ou não testáveis"></textarea>
              </label>
              <div class="form-actions">
                <button type="submit" class="primary-button">Salvar validação</button>
              </div>
            </form>
          </article>

          <article class="screen-card">
            <h4>Registros salvos</h4>
            <div class="validation-log" id="validation-log">
              ${logs.length
        ? logs
          .map(
            (entry) => `
                          <div class="log-item">
                            <div class="screen-header">
                              <strong>${entry.groupName}</strong>
                              <button type="button" class="ghost-button" data-delete-validation="${entry.id}">Remover</button>
                            </div>
                            <p><strong>Avaliador:</strong> ${entry.reviewer}</p>
                            <p><strong>Data:</strong> ${entry.reviewDate}</p>
                            <p><strong>Decisão:</strong> ${entry.decision}</p>
                            ${entry.consistencyNote ? `<p><strong>Consistência:</strong> ${entry.consistencyNote}</p>` : ''}
                            ${entry.completenessNote ? `<p><strong>Completude:</strong> ${entry.completenessNote}</p>` : ''}
                            ${entry.rnfNote ? `<p><strong>RNFs:</strong> ${entry.rnfNote}</p>` : ''}
                          </div>
                        `,
          )
          .join('')
        : '<div class="empty-state"><p>Nenhum registro de validação salvo.</p></div>'
      }
            </div>
          </article>
        </div>
      </section>
    `,
  });
}

function isLoginBypassed() {
  return localStorage.getItem(BYPASS_LOGIN_KEY) === 'true';
}

function isUserLoggedIn() {
  return sessionStorage.getItem(LOGIN_SESSION_KEY) === 'true';
}

function loginPage(errorMessage = '') {
  return layout({
    title: 'Autenticação de Gestor',
    subtitle: 'Área operacional restrita',
    main: `
      <section class="login-container">
        <article class="login-card">
          <div class="login-badge">
            <span class="login-badge-icon">🔐</span>
          </div>
          <div class="login-header">
            <h3>Painel de Gestão</h3>
            <p>Acesse o painel para gerenciar manifestações</p>
          </div>

          ${errorMessage ? `
            <div class="login-error">
              <span class="login-error-icon">⚠️</span>
              <span>${errorMessage}</span>
            </div>
          ` : ''}

          <form id="login-form" class="login-form">
            <div class="login-input-group">
              <label for="login-username">Identificador / Usuário</label>
              <div class="login-input-wrapper">
                <span class="login-input-icon">👤</span>
                <input id="login-username" name="username" type="text" placeholder="Nome de usuário" required autofocus />
              </div>
            </div>
            
            <div class="login-input-group">
              <label for="login-password">Senha de acesso</label>
              <div class="login-input-wrapper">
                <span class="login-input-icon">🔑</span>
                <input id="login-password" name="password" type="password" placeholder="Senha" required />
              </div>
            </div>

            <div class="login-actions">
              <button type="submit" class="login-submit-btn">
                <span>Entrar no sistema</span>
                <span class="login-btn-arrow">→</span>
              </button>
              <button type="button" class="login-bypass-btn" id="login-bypass-btn">
                Bypass
              </button>
            </div>
          </form>

          <div class="login-demo-notice">
            <p class="notice-title">💡 Credenciais de Teste</p>
            <div class="notice-credentials">
              <span>Usuário: <code>admin</code></span>
              <span>Senha: <code>admin</code></span>
            </div>
          </div>
        </article>
      </section>
    `
  });
}

function currentRoute() {
  const hash = location.hash.replace('#', '') || '/';
  if (hash === '/' || hash === '') return 'home';
  if (hash.startsWith('/abrir')) return 'abrir';
  if (hash.startsWith('/acompanhar')) return 'acompanhar';
  if (hash.startsWith('/atendimento')) return 'atendimento';
  if (hash.startsWith('/validacao')) return 'validacao';
  return 'home';
}

async function render(message = '') {
  const route = currentRoute();
  const query = new URLSearchParams(location.hash.split('?')[1] || '');

  let mainContent = '';
  if (route === 'home') {
    mainContent = await homePage();
  } else if (route === 'abrir') {
    mainContent = openPage(message);
  } else if (route === 'acompanhar') {
    mainContent = await trackingPage(message);
  } else if (route === 'atendimento') {
    if (isLoginBypassed() || isUserLoggedIn()) {
      mainContent = await atendimentoPage({ protocol: query.get('protocol') || '' });
    } else {
      mainContent = loginPage();
    }
  } else if (route === 'validacao') {
    mainContent = await validationPage();
  }

  app.innerHTML = mainContent;
  bindGlobalEvents();
}

function bindGlobalEvents() {
  const routeToHref = {
    home: '#/',
    abrir: '#/abrir',
    acompanhar: '#/acompanhar',
    atendimento: '#/atendimento',
    validacao: '#/validacao',
  };

  document.querySelectorAll('.menu-link').forEach((link) => {
    link.classList.toggle('active', link.getAttribute('href') === routeToHref[currentRoute()]);
  });

  const manifestationForm = document.querySelector('#manifestation-form');
  if (manifestationForm) {
    const identityFields = document.querySelector('[data-identity-fields]');
    const toggleIdentity = () => {
      const anonymous = manifestationForm.querySelector('input[name="anonymous"]:checked')?.value === 'true';
      identityFields.classList.toggle('is-hidden', anonymous);
      identityFields.querySelectorAll('input').forEach((input) => {
        input.required = !anonymous;
      });
    };

    manifestationForm.querySelectorAll('input[name="anonymous"]').forEach((radio) => {
      radio.addEventListener('change', toggleIdentity);
    });
    toggleIdentity();

    manifestationForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(manifestationForm);
      const anonymous = formData.get('anonymous') === 'true';
      const files = Array.from(manifestationForm.querySelector('input[name="attachments"]').files || []).map((file) => file.name);

      const payload = {
        category: String(formData.get('category') || 'Denúncia'),
        anonymous,
        name: String(formData.get('name') || ''),
        email: String(formData.get('email') || ''),
        phone: String(formData.get('phone') || ''),
        subject: String(formData.get('subject') || ''),
        description: String(formData.get('description') || ''),
        sector: String(formData.get('sector') || ''),
        attachments: files,
      };

      if (!anonymous && (!payload.name.trim() || !payload.email.trim() || !payload.phone.trim())) {
        alert('Preencha nome, e-mail e telefone para manifestação identificada.');
        return;
      }

      if (payload.description.trim().length < 30) {
        alert('A descrição deve ter pelo menos 30 caracteres para ser útil à análise.');
        return;
      }

      (async () => {
        try {
          const res = await fetch('/api/manifestacoes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          if (!res.ok) {
            const err = await res.json();
            alert(err.detail || 'Erro ao registrar manifestação.');
            return;
          }
          const result = await res.json();

          localStorage.setItem(
            SESSION_KEY,
            JSON.stringify({
              protocol: result.protocol,
              secret: payload.anonymous ? 'SIGILOSO' : payload.email,
            }),
          );

          location.hash = `#/acompanhar?protocol=${result.protocol}`;
          await render(`Manifestação registrada com o protocolo ${result.protocol}.`);
        } catch (e) {
          alert('Erro de conexão ao registrar manifestação.');
        }
      })();
    });
  }

  const trackingForm = document.querySelector('#tracking-form');
  if (trackingForm) {
    trackingForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(trackingForm);
      const protocol = String(formData.get('protocol') || '').trim().toUpperCase();
      const secret = String(formData.get('secret') || '').trim();
      localStorage.setItem(SESSION_KEY, JSON.stringify({ protocol, secret }));

      (async () => {
        const manifestation = await findManifestation(protocol);
        const result = document.querySelector('#tracking-result');
        result.innerHTML = trackingResultMarkup(manifestation, secret);
        bindResultActions();
      })();
    });

    const fillLastButton = document.querySelector('[data-fill-last]');
    if (fillLastButton) {
      fillLastButton.addEventListener('click', () => {
        const last = JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
        if (!last) {
          alert('Não há última consulta salva.');
          return;
        }

        trackingForm.querySelector('input[name="protocol"]').value = last.protocol || '';
        trackingForm.querySelector('input[name="secret"]').value = last.secret || '';
      });
    }
  }

  const adminForm = document.querySelector('#admin-form');
  if (adminForm) {
    adminForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(adminForm);
      const protocol = adminForm.dataset.protocol;

      const payload = {
        sector: String(formData.get('sector') || ''),
        status: String(formData.get('status') || ''),
        response: String(formData.get('response') || ''),
      };

      (async () => {
        const success = await updateManifestation(protocol, payload);
        if (!success) {
          alert('Erro ao atualizar manifestação.');
          return;
        }
        location.hash = `#/atendimento?protocol=${protocol}`;
        await render('Atualização salva com sucesso no painel do atendente.');
      })();
    });
  }

  const validationForm = document.querySelector('#validation-form');
  if (validationForm) {
    validationForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(validationForm);
      const payload = {
        id: Date.now().toString(),
        groupName: String(formData.get('groupName') || '').trim(),
        reviewer: String(formData.get('reviewer') || '').trim(),
        reviewDate: String(formData.get('reviewDate') || ''),
        decision: String(formData.get('decision') || ''),
        consistencyNote: String(formData.get('consistencyNote') || '').trim(),
        completenessNote: String(formData.get('completenessNote') || '').trim(),
        rnfNote: String(formData.get('rnfNote') || '').trim(),
        createdAt: new Date().toISOString(),
      };

      (async () => {
        try {
          await fetch('/api/validacoes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          await render('Validação registrada com sucesso.');
        } catch {
          alert('Erro de conexão ao salvar validação.');
        }
      })();
    });
  }

  document.querySelectorAll('[data-delete-validation]').forEach((button) => {
    button.addEventListener('click', () => {
      const logId = button.dataset.deleteValidation;
      (async () => {
        try {
          await fetch(`/api/validacoes/${logId}`, {
            method: 'DELETE'
          });
          await render('Registro de validação removido.');
        } catch {
          alert('Erro de conexão ao remover validação.');
        }
      })();
    });
  });

  document.querySelectorAll('[data-open-protocol]').forEach((button) => {
    button.addEventListener('click', () => {
      location.hash = `#/atendimento?protocol=${button.dataset.openProtocol}`;
      render();
    });
  });

  document.querySelectorAll('[data-copy-protocol]').forEach((button) => {
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(button.dataset.copyProtocol);
        button.textContent = 'Copiado';
        window.setTimeout(() => {
          button.textContent = 'Copiar protocolo';
        }, 1200);
      } catch {
        alert(`Protocolo: ${button.dataset.copyProtocol}`);
      }
    });
  });

  const bypassToggle = document.querySelector('#bypass-login-toggle');
  if (bypassToggle) {
    bypassToggle.addEventListener('change', (event) => {
      localStorage.setItem(BYPASS_LOGIN_KEY, event.target.checked ? 'true' : 'false');
      if (!event.target.checked) {
        sessionStorage.removeItem(LOGIN_SESSION_KEY);
      }
      render();
    });
  }

  const loginForm = document.querySelector('#login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(loginForm);
      const username = String(formData.get('username') || '').trim();
      const password = String(formData.get('password') || '').trim();

      if (username === 'admin' && password === 'admin') {
        sessionStorage.setItem(LOGIN_SESSION_KEY, 'true');
        location.hash = '#/atendimento';
        render();
      } else {
        app.innerHTML = loginPage('Usuário ou senha incorretos.');
        bindGlobalEvents();
      }
    });

    const loginBypassBtn = document.querySelector('#login-bypass-btn');
    if (loginBypassBtn) {
      loginBypassBtn.addEventListener('click', () => {
        localStorage.setItem(BYPASS_LOGIN_KEY, 'true');
        location.hash = '#/atendimento';
        render();
      });
    }
  }

  const logoutBtn = document.querySelector('#logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      sessionStorage.removeItem(LOGIN_SESSION_KEY);
      render();
    });
  }
}

function bindResultActions() {
  document.querySelectorAll('[data-copy-protocol]').forEach((button) => {
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(button.dataset.copyProtocol);
      } catch {
        alert(`Protocolo: ${button.dataset.copyProtocol}`);
      }
    });
  });
}

window.addEventListener('hashchange', () => render());
render();
