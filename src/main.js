import './styles.css';

const app = document.querySelector('#app');
const STORAGE_KEY = 'ouvidoria-publica.manifestacoes.v1';
const SESSION_KEY = 'ouvidoria-publica.ultima-consulta.v1';
const VALIDATION_LOG_KEY = 'ouvidoria-publica.validacoes.v1';

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

function readValidationLogs() {
  try {
    const raw = localStorage.getItem(VALIDATION_LOG_KEY);
    if (!raw) {
      return [];
    }

    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeValidationLogs(logs) {
  localStorage.setItem(VALIDATION_LOG_KEY, JSON.stringify(logs));
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

function seedManifestations() {
  const sample = [
    createManifestationRecord({
      category: 'Denúncia',
      anonymous: false,
      name: 'Maria Santos',
      email: 'maria@exemplo.gov.br',
      phone: '(11) 98888-9999',
      subject: 'Lâmpada queimada na praça central',
      description: 'A iluminação pública da praça central está sem funcionar há mais de uma semana.',
      sector: 'Mobilidade',
      attachments: ['foto-praca.jpg'],
    }),
    createManifestationRecord({
      category: 'Solicitação',
      anonymous: true,
      subject: 'Pedido de poda de árvore',
      description: 'Galhos estão encostando na fiação e oferecendo risco para pedestres.',
      sector: 'Meio ambiente',
      attachments: [],
    }),
  ];

  sample[0].status = 'Em análise';
  sample[0].history.push({
    status: 'Em análise',
    date: new Date().toISOString(),
    note: 'Manifestação encaminhada para análise técnica.',
  });
  sample[1].status = 'Encaminhada ao setor';
  sample[1].history.push({
    status: 'Encaminhada ao setor',
    date: new Date().toISOString(),
    note: 'Solicitação encaminhada ao setor responsável.',
  });

  localStorage.setItem(STORAGE_KEY, JSON.stringify(sample));
  return sample;
}

function readManifestations() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return seedManifestations();
    }

    const data = JSON.parse(raw);
    return Array.isArray(data) ? data : seedManifestations();
  } catch {
    return seedManifestations();
  }
}

function writeManifestations(manifestations) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(manifestations));
}

function createProtocol() {
  const now = new Date();
  const stamp = now.toISOString().replace(/[-:TZ.]/g, '').slice(2, 14);
  const random = Math.random().toString(36).slice(2, 6).toUpperCase();
  return `OP-${stamp}-${random}`;
}

function createAccessCode() {
  return Math.random().toString(36).slice(2, 8).toUpperCase();
}

function createManifestationRecord(formValues) {
  const now = new Date().toISOString();
  const anonymous = Boolean(formValues.anonymous);
  const protocol = createProtocol();
  const accessCode = anonymous ? createAccessCode() : '';
  const subject = formValues.subject?.trim() || 'Sem assunto';

  return {
    protocol,
    accessCode,
    category: formValues.category,
    anonymous,
    name: anonymous ? 'Sigiloso' : formValues.name.trim(),
    email: anonymous ? '' : formValues.email.trim(),
    phone: anonymous ? '' : formValues.phone.trim(),
    subject,
    description: formValues.description.trim(),
    sector: formValues.sector,
    attachments: formValues.attachments,
    status: 'Recebida',
    response: '',
    createdAt: now,
    updatedAt: now,
    history: [
      {
        status: 'Recebida',
        date: now,
        note: 'Manifestação criada no portal.',
      },
    ],
  };
}

function findManifestation(protocol) {
  return readManifestations().find((item) => item.protocol === protocol.trim().toUpperCase());
}

function updateManifestation(protocol, patch) {
  const manifestations = readManifestations();
  const index = manifestations.findIndex((item) => item.protocol === protocol);

  if (index === -1) {
    return null;
  }

  manifestations[index] = {
    ...manifestations[index],
    ...patch,
    updatedAt: new Date().toISOString(),
  };

  writeManifestations(manifestations);
  return manifestations[index];
}

function layout({ main, title, subtitle }) {
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
          <a class="menu-link" href="#/">Início</a>
          <a class="menu-link" href="#/abrir">Abrir manifestação</a>
          <a class="menu-link" href="#/acompanhar">Acompanhar protocolo</a>
          <a class="menu-link" href="#/atendimento">Painel do atendente</a>
          <a class="menu-link" href="#/validacao">Validação em campo</a>
        </nav>

        <section class="side-card">
          <p class="eyebrow">Fluxo real</p>
          <strong>Ouvidoria Pública</strong>
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

function homePage() {
  const manifestations = readManifestations();
  const openCount = manifestations.filter((item) => item.status !== 'Concluída').length;
  const closedCount = manifestations.filter((item) => item.status === 'Concluída').length;

  return layout({
    title: 'Portal de gerenciamento de manifestações públicas',
    subtitle: 'Atendimento digital',
    main: `
      <section class="hero hero-real">
        <div>
          <p class="eyebrow">Ouvidoria Digital</p>
          <h3>Portal de atendimento ao cidadão.</h3>
          <div class="hero-actions">
            <a class="primary-button" href="#/abrir">Abrir manifestação</a>
            <a class="ghost-button" href="#/acompanhar">Consultar protocolo</a>
          </div>
        </div>

        <div class="hero-panel real-panel">
          <p class="panel-label">Situação da base</p>
          <strong>${manifestations.length} manifestações salvas</strong>
          <div class="panel-metrics">
            <span>${openCount} em andamento</span>
            <span>${closedCount} concluídas</span>
            <span>${manifestations.filter((item) => item.anonymous).length} anônimas</span>
          </div>
        </div>
      </section>

      <section class="cards-grid">
        ${[
          ['Abrir manifestação', ''],
          ['Acompanhar andamento', ''],
          ['Responder no atendimento', ''],
          ['Validar em campo', ''],
        ]
          .map(
            ([title, text], index) => `
              <article class="feature-card" style="--accent: var(${index % 2 === 0 ? 'citrine' : 'sky'})">
                <h3>${title}</h3>
                ${text ? `<p>${text}</p>` : ''}
              </article>
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

        <aside class="screen-card side-stack">
          <div class="callout">
            <strong>Registro de manifestação</strong>
          </div>
          <div class="callout muted-callout">
            <strong>Atendimento digital</strong>
          </div>
        </aside>
      </section>
    `,
  });
}

function trackingPage(message = '') {
  const savedQuery = JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
  const latest = savedQuery ? findManifestation(savedQuery.protocol) : null;

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
                Protocolo
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

        <aside class="screen-card side-stack">
          <div class="callout">
            <strong>Consulta de manifestação</strong>
          </div>
          <div class="callout muted-callout">
            <strong>Histórico e resposta</strong>
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

  const secretMatches = manifestation.anonymous
    ? providedSecret?.trim().toUpperCase() === manifestation.accessCode
    : providedSecret?.trim().toLowerCase() === manifestation.email.toLowerCase();

  if (!secretMatches) {
    return `
      <div class="empty-state error-state">
        <h3>Dados de acesso incorretos</h3>
        <p>O protocolo existe, mas a credencial informada não confere com o registro.</p>
      </div>
    `;
  }

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

function atendimentoPage(filters = {}) {
  const all = readManifestations();
  const selectedProtocol = filters.protocol || all[0]?.protocol || '';
  const selected = all.find((item) => item.protocol === selectedProtocol) || all[0] || null;

  return layout({
    title: 'Painel do atendente',
    subtitle: 'Área interna',
    main: `
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

function validationPage() {
  const logs = readValidationLogs();
  const covered = functionalCoverage.filter((item) => item.status === 'atendido').length;
  const partial = functionalCoverage.filter((item) => item.status === 'parcial').length;
  const missing = functionalCoverage.filter((item) => item.status === 'nao_atendido').length;

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
          <p>${consistencyChecks.filter((item) => item.status === 'ok').length} consistentes</p>
          <p>${consistencyChecks.filter((item) => item.status === 'atencao').length} com atenção</p>
          <p>${consistencyChecks.filter((item) => item.status === 'inconsistente').length} inconsistentes</p>
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
            ${consistencyChecks
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
                ${functionalCoverage
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
              ${
                logs.length
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

function currentRoute() {
  const hash = location.hash.replace('#', '') || '/';
  if (hash === '/' || hash === '') return 'home';
  if (hash.startsWith('/abrir')) return 'abrir';
  if (hash.startsWith('/acompanhar')) return 'acompanhar';
  if (hash.startsWith('/atendimento')) return 'atendimento';
  if (hash.startsWith('/validacao')) return 'validacao';
  return 'home';
}

function render(message = '') {
  const route = currentRoute();
  const query = new URLSearchParams(location.hash.split('?')[1] || '');

  const views = {
    home: () => homePage(),
    abrir: () => openPage(message),
    acompanhar: () => trackingPage(message),
    atendimento: () => atendimentoPage({ protocol: query.get('protocol') || '' }),
    validacao: () => validationPage(),
  };

  app.innerHTML = views[route]();
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

      const record = createManifestationRecord(payload);
      const manifestations = readManifestations();
      manifestations.unshift(record);
      writeManifestations(manifestations);

      localStorage.setItem(
        SESSION_KEY,
        JSON.stringify({
          protocol: record.protocol,
          secret: record.anonymous ? record.accessCode : record.email,
        }),
      );

      location.hash = `#/acompanhar?protocol=${record.protocol}`;
      render(`Manifestação registrada com o protocolo ${record.protocol}.`);
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
      const manifestation = findManifestation(protocol);
      const result = document.querySelector('#tracking-result');
      result.innerHTML = trackingResultMarkup(manifestation, secret);
      bindResultActions();
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
      const updated = updateManifestation(protocol, {
        sector: String(formData.get('sector') || ''),
        status: String(formData.get('status') || ''),
        response: String(formData.get('response') || ''),
      });

      if (!updated) {
        alert('Manifestação não encontrada.');
        return;
      }

      const manifestations = readManifestations();
      const current = manifestations.find((item) => item.protocol === protocol);
      current.history.push({
        status: updated.status,
        date: new Date().toISOString(),
        note: 'Atualização registrada pelo painel do atendente.',
      });
      if (updated.response) {
        current.history.push({
          status: 'Resposta registrada',
          date: new Date().toISOString(),
          note: updated.response,
        });
      }
      writeManifestations(manifestations);
      location.hash = `#/atendimento?protocol=${protocol}`;
      render('Atualização salva com sucesso no painel do atendente.');
    });
  }

  const validationForm = document.querySelector('#validation-form');
  if (validationForm) {
    validationForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(validationForm);
      const logs = readValidationLogs();
      logs.unshift({
        id: Date.now().toString(),
        groupName: String(formData.get('groupName') || '').trim(),
        reviewer: String(formData.get('reviewer') || '').trim(),
        reviewDate: String(formData.get('reviewDate') || ''),
        decision: String(formData.get('decision') || ''),
        consistencyNote: String(formData.get('consistencyNote') || '').trim(),
        completenessNote: String(formData.get('completenessNote') || '').trim(),
        rnfNote: String(formData.get('rnfNote') || '').trim(),
        createdAt: new Date().toISOString(),
      });
      writeValidationLogs(logs);
      render('Validação registrada com sucesso.');
    });
  }

  document.querySelectorAll('[data-delete-validation]').forEach((button) => {
    button.addEventListener('click', () => {
      const logs = readValidationLogs().filter((entry) => entry.id !== button.dataset.deleteValidation);
      writeValidationLogs(logs);
      render('Registro de validação removido.');
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
