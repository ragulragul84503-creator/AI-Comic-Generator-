/**
 * ComicCraft — AI Comic Story Creator
 * Main Client Controller & State Machine
 */

(function () {
  'use strict';

  // State
  const state = {
    currentComic: null,
    pdfUrl: null,
    isGenerating: false,
    isExportingPdf: false,
    selectedStyle: 'Anime',
    selectedTone: 'Adventure',
    selectedPanels: 5,
    selectedSetting: 'Enchanted Forest',
    editingPanelIndex: null
  };

  // DOM Elements
  const elements = {
    // Nav
    navToggle: document.getElementById('nav-toggle'),
    navLinks: document.getElementById('nav-links'),

    // Form
    comicForm: document.getElementById('comic-craft-form'),
    promptInput: document.getElementById('story_prompt'),
    charCounter: document.getElementById('char-counter'),
    characterInput: document.getElementById('character_name'),
    settingSelect: document.getElementById('setting_select'),
    customSettingWrap: document.getElementById('custom_setting_wrap'),
    customSettingInput: document.getElementById('custom_setting_input'),
    surpriseBtn: document.getElementById('btn-surprise-me'),
    clearBtn: document.getElementById('btn-clear-all'),
    generateBtn: document.getElementById('btn-generate-main'),

    // Tone & Style Selectors
    toneCards: document.querySelectorAll('.tone-card'),
    styleCards: document.querySelectorAll('.style-card'),
    panelPills: document.querySelectorAll('.panel-pill'),

    // Live Preview Panel
    liveTagChar: document.getElementById('live-tag-char'),
    liveTagSetting: document.getElementById('live-tag-setting'),
    liveTagTone: document.getElementById('live-tag-tone'),
    liveTagStyle: document.getElementById('live-tag-style'),
    liveTagPanels: document.getElementById('live-tag-panels'),
    livePreviewSlot: document.getElementById('live-preview-slot'),
    liveSpeechDemo: document.getElementById('live-speech-demo'),

    // Generation Overlay Modal
    genOverlay: document.getElementById('generation-overlay'),
    genPercentFill: document.getElementById('gen-percent-fill'),
    genPercentText: document.getElementById('gen-percent-text'),
    genStageNote: document.getElementById('gen-stage-note'),
    genStagesList: document.getElementById('gen-stages-list'),

    // Preview Section
    previewSection: document.getElementById('preview-section'),
    previewComicTitle: document.getElementById('preview-comic-title'),
    previewComicSubtitle: document.getElementById('preview-comic-subtitle'),
    panelsContainer: document.getElementById('comic-panels-container'),
    sidebarChar: document.getElementById('sidebar-char'),
    sidebarSetting: document.getElementById('sidebar-setting'),
    sidebarTone: document.getElementById('sidebar-tone'),
    sidebarStyle: document.getElementById('sidebar-style'),
    sidebarPanels: document.getElementById('sidebar-panels'),
    sidebarSource: document.getElementById('sidebar-source'),

    // Preview Action Buttons
    downloadPdfBtn: document.getElementById('btn-download-pdf'),
    previewPdfBtn: document.getElementById('btn-preview-pdf'),
    regenerateBtn: document.getElementById('btn-regenerate-all'),
    newComicBtn: document.getElementById('btn-new-comic'),
    shareBtn: document.getElementById('btn-share-comic'),

    // Export Success Overlay
    successOverlay: document.getElementById('success-overlay'),
    successComicTitle: document.getElementById('success-comic-title'),
    successDownloadAgainBtn: document.getElementById('btn-success-download-again'),
    successNewComicBtn: document.getElementById('btn-success-new-comic'),
    successBackPreviewBtn: document.getElementById('btn-success-back-preview'),

    // Edit Panel Text Modal
    editModalOverlay: document.getElementById('edit-modal-overlay'),
    editPanelNumber: document.getElementById('edit-panel-number'),
    editCaptionInput: document.getElementById('edit-caption-input'),
    editDialogueInput: document.getElementById('edit-dialogue-input'),
    saveEditBtn: document.getElementById('btn-save-panel-edit'),
    cancelEditBtn: document.getElementById('btn-cancel-panel-edit'),

    // Toast Container
    toastContainer: document.getElementById('toast-container')
  };

  // ==========================================
  // INITIALIZATION
  // ==========================================
  function init() {
    setupNavigation();
    setupFormUX();
    setupToneAndStyleSelectors();
    setupPanelCountSelector();
    setupPreviewActions();
    setupSampleComicCards();
    updateLivePreview();
  }

  // ==========================================
  // NAVIGATION & MOBILE MENU
  // ==========================================
  function setupNavigation() {
    if (elements.navToggle) {
      elements.navToggle.addEventListener('click', () => {
        elements.navLinks.classList.toggle('active');
      });
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener('click', function (e) {
        const targetId = this.getAttribute('href').substring(1);
        const targetEl = document.getElementById(targetId);
        if (targetEl) {
          e.preventDefault();
          if (elements.navLinks) elements.navLinks.classList.remove('active');
          targetEl.scrollIntoView({ behavior: 'smooth' });
        }
      });
    });
  }

  // ==========================================
  // FORM INTERACTIONS & VALIDATION
  // ==========================================
  function setupFormUX() {
    // Character Counter
    if (elements.promptInput) {
      elements.promptInput.addEventListener('input', () => {
        const len = elements.promptInput.value.length;
        elements.charCounter.textContent = `${len} / 1000`;
        clearFieldError(elements.promptInput);
      });
    }

    if (elements.characterInput) {
      elements.characterInput.addEventListener('input', () => {
        clearFieldError(elements.characterInput);
        updateLivePreview();
      });
    }

    // Setting dropdown change
    if (elements.settingSelect) {
      elements.settingSelect.addEventListener('change', () => {
        const val = elements.settingSelect.value;
        state.selectedSetting = val;
        if (val === 'Custom') {
          elements.customSettingWrap.classList.add('active');
        } else {
          elements.customSettingWrap.classList.remove('active');
        }
        clearFieldError(elements.settingSelect);
        updateLivePreview();
      });
    }

    if (elements.customSettingInput) {
      elements.customSettingInput.addEventListener('input', () => {
        updateLivePreview();
      });
    }

    // Surprise Me Button
    if (elements.surpriseBtn) {
      elements.surpriseBtn.addEventListener('click', async () => {
        try {
          elements.surpriseBtn.disabled = true;
          elements.surpriseBtn.textContent = '🎲 Thinking...';
          const res = await fetch('/api/surprise-prompt');
          const data = await res.json();
          if (data) {
            elements.promptInput.value = data.prompt || '';
            elements.characterInput.value = data.character || 'Leo';
            elements.charCounter.textContent = `${elements.promptInput.value.length} / 1000`;

            // Set setting
            elements.settingSelect.value = data.setting || 'Enchanted Forest';
            state.selectedSetting = data.setting || 'Enchanted Forest';
            elements.customSettingWrap.classList.remove('active');

            // Select tone
            selectTone(data.tone || 'Adventure');

            // Select style
            selectArtStyle(data.art_style || 'Anime');

            // Panels count
            selectPanelsCount(data.panels_count || 5);

            clearAllErrors();
            updateLivePreview();
            showToast('🎲 Surprise idea loaded! Ready to generate.', 'success');
          }
        } catch (err) {
          showToast('Could not load surprise prompt.', 'error');
        } finally {
          elements.surpriseBtn.disabled = false;
          elements.surpriseBtn.textContent = '🎲 Surprise Me';
        }
      });
    }

    // Clear All Button
    if (elements.clearBtn) {
      elements.clearBtn.addEventListener('click', () => {
        elements.promptInput.value = '';
        elements.characterInput.value = '';
        elements.charCounter.textContent = '0 / 1000';
        elements.settingSelect.value = 'Enchanted Forest';
        state.selectedSetting = 'Enchanted Forest';
        elements.customSettingWrap.classList.remove('active');
        if (elements.customSettingInput) elements.customSettingInput.value = '';
        selectTone('Adventure');
        selectArtStyle('Anime');
        selectPanelsCount(5);
        clearAllErrors();
        updateLivePreview();
        showToast('Form cleared.', 'success');
      });
    }

    // Form Submit
    if (elements.comicForm) {
      elements.comicForm.addEventListener('submit', (e) => {
        e.preventDefault();
        startComicGeneration();
      });
    }
  }

  function validateForm() {
    let isValid = true;
    clearAllErrors();

    const promptVal = elements.promptInput.value.trim();
    if (!promptVal || promptVal.length < 5) {
      setFieldError(elements.promptInput, 'Please provide a story prompt (at least 5 characters).');
      isValid = false;
    }

    const charVal = elements.characterInput.value.trim();
    if (!charVal) {
      setFieldError(elements.characterInput, 'Please enter a character name.');
      isValid = false;
    }

    if (elements.settingSelect.value === 'Custom') {
      const customVal = elements.customSettingInput ? elements.customSettingInput.value.trim() : '';
      if (!customVal) {
        setFieldError(elements.customSettingInput, 'Please describe your custom setting.');
        isValid = false;
      }
    }

    return isValid;
  }

  function setFieldError(inputEl, msg) {
    const parent = inputEl.closest('.form-group');
    if (parent) {
      parent.classList.add('has-error');
      const errEl = parent.querySelector('.form-error-msg');
      if (errEl) errEl.textContent = msg;
    }
  }

  function clearFieldError(inputEl) {
    const parent = inputEl.closest('.form-group');
    if (parent) {
      parent.classList.remove('has-error');
    }
  }

  function clearAllErrors() {
    document.querySelectorAll('.form-group.has-error').forEach((fg) => {
      fg.classList.remove('has-error');
    });
  }

  // ==========================================
  // TONE & ART STYLE SELECTORS
  // ==========================================
  function setupToneAndStyleSelectors() {
    // Tone Cards
    elements.toneCards.forEach((card) => {
      card.addEventListener('click', () => {
        const tone = card.getAttribute('data-tone');
        selectTone(tone);
      });
    });

    // Style Cards
    elements.styleCards.forEach((card) => {
      card.addEventListener('click', () => {
        const style = card.getAttribute('data-style');
        selectArtStyle(style);
      });
    });
  }

  function selectTone(tone) {
    state.selectedTone = tone;
    elements.toneCards.forEach((c) => {
      if (c.getAttribute('data-tone') === tone) {
        c.classList.add('selected');
      } else {
        c.classList.remove('selected');
      }
    });
    updateLivePreview();
  }

  function selectArtStyle(style) {
    state.selectedStyle = style;
    elements.styleCards.forEach((c) => {
      if (c.getAttribute('data-style') === style) {
        c.classList.add('selected');
      } else {
        c.classList.remove('selected');
      }
    });
    updateLivePreview();
  }

  function setupPanelCountSelector() {
    elements.panelPills.forEach((pill) => {
      pill.addEventListener('click', () => {
        const count = parseInt(pill.getAttribute('data-panels'), 10);
        selectPanelsCount(count);
      });
    });
  }

  function selectPanelsCount(count) {
    state.selectedPanels = count;
    elements.panelPills.forEach((p) => {
      if (parseInt(p.getAttribute('data-panels'), 10) === count) {
        p.classList.add('selected');
      } else {
        p.classList.remove('selected');
      }
    });
    updateLivePreview();
  }

  // ==========================================
  // LIVE PREVIEW SIDEBAR UPDATES
  // ==========================================
  function updateLivePreview() {
    const charName = elements.characterInput.value.trim() || 'Hero';
    let settingName = state.selectedSetting;
    if (settingName === 'Custom' && elements.customSettingInput) {
      settingName = elements.customSettingInput.value.trim() || 'Custom World';
    }

    if (elements.liveTagChar) elements.liveTagChar.textContent = charName;
    if (elements.liveTagSetting) elements.liveTagSetting.textContent = settingName;
    if (elements.liveTagTone) elements.liveTagTone.textContent = state.selectedTone;
    if (elements.liveTagStyle) elements.liveTagStyle.textContent = state.selectedStyle;
    if (elements.liveTagPanels) elements.liveTagPanels.textContent = `${state.selectedPanels} Panels`;

    if (elements.liveSpeechDemo) {
      elements.liveSpeechDemo.innerHTML = `<span style="color:#2563EB; font-weight:800;">${charName.toUpperCase()}:</span> "The journey begins here!"`;
    }

    // Update preview slot background with active style card thumb
    const activeStyleCard = document.querySelector(`.style-card[data-style="${state.selectedStyle}"]`);
    if (activeStyleCard && elements.livePreviewSlot) {
      const thumb = activeStyleCard.querySelector('.style-thumb');
      if (thumb) {
        elements.livePreviewSlot.innerHTML = thumb.innerHTML;
      }
    }
  }

  // ==========================================
  // AI GENERATION PIPELINE (MODAL EXPERIENCE)
  // ==========================================
  async function startComicGeneration() {
    if (!validateForm() || state.isGenerating) return;

    state.isGenerating = true;
    elements.generateBtn.disabled = true;
    elements.generateBtn.innerHTML = `<span>⏳</span> Creating Comic...`;

    // Open Full-screen Generation Overlay
    elements.genOverlay.classList.add('active');

    const promptVal = elements.promptInput.value.trim();
    const charVal = elements.characterInput.value.trim();
    const settingVal = elements.settingSelect.value === 'Custom'
      ? (elements.customSettingInput ? elements.customSettingInput.value.trim() : 'Custom')
      : elements.settingSelect.value;

    const requestPayload = {
      story_prompt: promptVal,
      character_name: charVal,
      setting: settingVal,
      tone: state.selectedTone,
      art_style: state.selectedStyle,
      panels_count: state.selectedPanels
    };

    // Stage progression runner
    const stages = [
      { pct: 15, text: 'Understanding your story & character arc...', itemIdx: 0 },
      { pct: 35, text: `Building the ${state.selectedPanels}-panel outline...`, itemIdx: 1 },
      { pct: 55, text: 'Writing narration and character dialogue...', itemIdx: 2 },
      { pct: 75, text: `Creating panel illustrations in ${state.selectedStyle} style...`, itemIdx: 3 },
      { pct: 90, text: 'Building your comic layout...', itemIdx: 4 },
      { pct: 98, text: 'Preparing PDF export...', itemIdx: 5 }
    ];

    let currentStageIndex = 0;
    resetGenerationStages();

    const stageInterval = setInterval(() => {
      if (currentStageIndex < stages.length) {
        const st = stages[currentStageIndex];
        setGenerationProgress(st.pct, st.text, st.itemIdx);
        currentStageIndex++;
      }
    }, 900);

    try {
      const response = await fetch('/generate-comic/json', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestPayload)
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Server error occurred during generation.');
      }

      // Finish stages smoothly
      clearInterval(stageInterval);
      setGenerationProgress(100, 'Comic successfully assembled!', 5);

      setTimeout(() => {
        elements.genOverlay.classList.remove('active');
        state.isGenerating = false;
        elements.generateBtn.disabled = false;
        elements.generateBtn.innerHTML = `<span>✨</span> Generate My Comic`;

        // Load and render comic
        state.currentComic = data.comic;
        renderComicPreview(data.comic);

        // Scroll to preview section
        elements.previewSection.classList.add('active');
        elements.previewSection.scrollIntoView({ behavior: 'smooth' });

        showToast('Your comic is ready! Review panels below.', 'success');
      }, 700);

    } catch (err) {
      clearInterval(stageInterval);
      elements.genOverlay.classList.remove('active');
      state.isGenerating = false;
      elements.generateBtn.disabled = false;
      elements.generateBtn.innerHTML = `<span>✨</span> Generate My Comic`;

      showToast(`Error: ${err.message}`, 'error');
    }
  }

  function resetGenerationStages() {
    const items = elements.genStagesList.querySelectorAll('.stage-item');
    items.forEach((item, idx) => {
      item.className = 'stage-item';
      const icon = item.querySelector('.stage-icon');
      if (icon) icon.textContent = '○';
    });
  }

  function setGenerationProgress(percent, noteText, activeItemIndex) {
    if (elements.genPercentFill) elements.genPercentFill.style.width = `${percent}%`;
    if (elements.genPercentText) elements.genPercentText.textContent = `${percent}%`;
    if (elements.genStageNote) elements.genStageNote.textContent = noteText;

    const items = elements.genStagesList.querySelectorAll('.stage-item');
    items.forEach((item, idx) => {
      const icon = item.querySelector('.stage-icon');
      if (idx < activeItemIndex) {
        item.className = 'stage-item completed';
        if (icon) icon.textContent = '✓';
      } else if (idx === activeItemIndex) {
        item.className = 'stage-item active';
        if (icon) icon.textContent = '→';
      } else {
        item.className = 'stage-item';
        if (icon) icon.textContent = '○';
      }
    });
  }

  // ==========================================
  // COMIC PREVIEW RENDERING
  // ==========================================
  function renderComicPreview(comic) {
    if (!comic) return;

    // Header info
    if (elements.previewComicTitle) elements.previewComicTitle.textContent = comic.title;
    if (elements.previewComicSubtitle) {
      elements.previewComicSubtitle.textContent = `A ${comic.art_style} story starring ${comic.character} in the ${comic.setting}.`;
    }

    // Sidebar details
    if (elements.sidebarChar) elements.sidebarChar.textContent = comic.character;
    if (elements.sidebarSetting) elements.sidebarSetting.textContent = comic.setting;
    if (elements.sidebarTone) elements.sidebarTone.textContent = comic.tone;
    if (elements.sidebarStyle) elements.sidebarStyle.textContent = comic.art_style;
    if (elements.sidebarPanels) elements.sidebarPanels.textContent = `${comic.panels ? comic.panels.length : 5} Panels`;
    if (elements.sidebarSource) {
      elements.sidebarSource.textContent = comic.source || 'AI Powered';
    }

    // Panels container
    elements.panelsContainer.innerHTML = '';

    (comic.panels || []).forEach((panel, index) => {
      const panelBox = document.createElement('div');
      panelBox.className = 'comic-panel-box';
      panelBox.setAttribute('data-panel-idx', index);

      const pNum = panel.number || (index + 1);
      const pTitle = panel.title || `Panel 0${pNum}`;
      const caption = panel.caption || '';
      const dialogue = panel.dialogue || '';
      const sceneDesc = panel.scene_description || '';
      const imgSrc = panel.image || '';

      panelBox.innerHTML = `
        <div class="panel-top-banner">
          <span class="panel-badge">PANEL 0${pNum}</span>
          <span class="panel-title-text">${escapeHtml(pTitle)}</span>
        </div>

        <div class="panel-img-container">
          <div class="panel-hover-actions">
            <button class="panel-action-btn btn-regen-panel" data-panel-idx="${index}" title="Regenerate artwork">🔄 Regen</button>
            <button class="panel-action-btn btn-edit-panel" data-panel-idx="${index}" title="Edit caption and dialogue">✏️ Edit Text</button>
            <button class="panel-action-btn btn-dl-img" data-panel-idx="${index}" title="Download panel image">🖼️ Download</button>
          </div>
          <img src="${imgSrc}" alt="${escapeHtml(pTitle)}" loading="lazy" />
        </div>

        <div class="panel-content-body">
          <div class="caption-box">
            <span class="caption-tag">NARRATION</span>
            <p class="panel-caption-text">"${escapeHtml(caption)}"</p>
          </div>

          <div class="speech-bubble">
            <p class="panel-dialogue-text">${formatDialogue(dialogue, comic.character)}</p>
          </div>

          <div class="scene-details-drawer">
            <strong>Scene:</strong> ${escapeHtml(sceneDesc)}
          </div>
        </div>
      `;

      elements.panelsContainer.appendChild(panelBox);
    });

    attachPanelActionListeners();
  }

  function formatDialogue(text, fallbackChar) {
    if (!text) return `<strong>${escapeHtml(fallbackChar.toUpperCase())}:</strong> "..."`;
    // If dialogue contains "CHARACTER:", format speaker name
    if (text.includes(':')) {
      const parts = text.split(':');
      const speaker = parts[0].trim();
      const quote = parts.slice(1).join(':').trim();
      return `<strong class="dialogue-speaker">${escapeHtml(speaker)}:</strong> ${escapeHtml(quote)}`;
    }
    return escapeHtml(text);
  }

  function attachPanelActionListeners() {
    // Regenerate individual panel
    document.querySelectorAll('.btn-regen-panel').forEach((btn) => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const pIdx = parseInt(btn.getAttribute('data-panel-idx'), 10);
        await regenerateSinglePanel(pIdx);
      });
    });

    // Edit Panel Text
    document.querySelectorAll('.btn-edit-panel').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const pIdx = parseInt(btn.getAttribute('data-panel-idx'), 10);
        openEditPanelModal(pIdx);
      });
    });

    // Download Panel Image
    document.querySelectorAll('.btn-dl-img').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const pIdx = parseInt(btn.getAttribute('data-panel-idx'), 10);
        downloadPanelImage(pIdx);
      });
    });
  }

  // ==========================================
  // PANEL ACTIONS (REGEN, EDIT, DOWNLOAD)
  // ==========================================
  async function regenerateSinglePanel(panelIndex) {
    if (!state.currentComic || !state.currentComic.panels[panelIndex]) return;

    const panel = state.currentComic.panels[panelIndex];
    showToast(`Regenerating Panel ${panelIndex + 1}...`, 'info');

    try {
      const res = await fetch('/test-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: panel.image_prompt || panel.scene_description || 'Heroic comic scene',
          art_style: state.currentComic.art_style,
          setting: state.currentComic.setting,
          character_name: state.currentComic.character
        })
      });
      const data = await res.json();
      if (data && data.success && data.image) {
        panel.image = data.image;
        renderComicPreview(state.currentComic);
        showToast(`Panel ${panelIndex + 1} artwork refreshed!`, 'success');
      } else {
        throw new Error('Image generation failed.');
      }
    } catch (err) {
      showToast(`Could not regenerate panel: ${err.message}`, 'error');
    }
  }

  function openEditPanelModal(panelIndex) {
    if (!state.currentComic || !state.currentComic.panels[panelIndex]) return;

    state.editingPanelIndex = panelIndex;
    const panel = state.currentComic.panels[panelIndex];

    elements.editPanelNumber.textContent = `Panel 0${panelIndex + 1}`;
    elements.editCaptionInput.value = panel.caption || '';
    elements.editDialogueInput.value = panel.dialogue || '';

    elements.editModalOverlay.classList.add('active');
  }

  function downloadPanelImage(panelIndex) {
    if (!state.currentComic || !state.currentComic.panels[panelIndex]) return;
    const panel = state.currentComic.panels[panelIndex];
    const imgSrc = panel.image;

    const a = document.createElement('a');
    a.href = imgSrc;
    a.download = `ComicCraft_Panel_${panelIndex + 1}.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast(`Panel ${panelIndex + 1} image downloaded!`, 'success');
  }

  // ==========================================
  // PDF EXPORT WORKFLOW
  // ==========================================
  function setupPreviewActions() {
    // Download PDF Button
    if (elements.downloadPdfBtn) {
      elements.downloadPdfBtn.addEventListener('click', async () => {
        await executePdfExport(false);
      });
    }

    // Preview PDF Button
    if (elements.previewPdfBtn) {
      elements.previewPdfBtn.addEventListener('click', async () => {
        await executePdfExport(true);
      });
    }

    // Regenerate All Button
    if (elements.regenerateBtn) {
      elements.regenerateBtn.addEventListener('click', () => {
        startComicGeneration();
      });
    }

    // Create Another Comic Button
    if (elements.newComicBtn) {
      elements.newComicBtn.addEventListener('click', () => {
        window.scrollTo({ top: document.getElementById('workspace').offsetTop - 60, behavior: 'smooth' });
      });
    }

    // Share Button
    if (elements.shareBtn) {
      elements.shareBtn.addEventListener('click', () => {
        if (navigator.clipboard) {
          navigator.clipboard.writeText(window.location.href);
          showToast('Comic link copied to clipboard!', 'success');
        } else {
          showToast('Share link: ' + window.location.href, 'info');
        }
      });
    }

    // Edit Modal Buttons
    if (elements.cancelEditBtn) {
      elements.cancelEditBtn.addEventListener('click', () => {
        elements.editModalOverlay.classList.remove('active');
      });
    }

    if (elements.saveEditBtn) {
      elements.saveEditBtn.addEventListener('click', () => {
        if (state.editingPanelIndex !== null && state.currentComic) {
          const panel = state.currentComic.panels[state.editingPanelIndex];
          panel.caption = elements.editCaptionInput.value.trim();
          panel.dialogue = elements.editDialogueInput.value.trim();
          elements.editModalOverlay.classList.remove('active');
          renderComicPreview(state.currentComic);
          showToast(`Panel 0${state.editingPanelIndex + 1} updated!`, 'success');
        }
      });
    }

    // Export Success Overlay Actions
    if (elements.successDownloadAgainBtn) {
      elements.successDownloadAgainBtn.addEventListener('click', () => {
        if (state.pdfUrl) {
          triggerFileDownload(state.pdfUrl);
        }
      });
    }

    if (elements.successNewComicBtn) {
      elements.successNewComicBtn.addEventListener('click', () => {
        elements.successOverlay.classList.remove('active');
        window.scrollTo({ top: document.getElementById('workspace').offsetTop - 60, behavior: 'smooth' });
      });
    }

    if (elements.successBackPreviewBtn) {
      elements.successBackPreviewBtn.addEventListener('click', () => {
        elements.successOverlay.classList.remove('active');
      });
    }
  }

  async function executePdfExport(openPreviewTab = false) {
    if (!state.currentComic || state.isExportingPdf) return;

    state.isExportingPdf = true;
    const originalText = elements.downloadPdfBtn.innerHTML;
    elements.downloadPdfBtn.disabled = true;
    elements.downloadPdfBtn.innerHTML = `<span>⏳</span> Preparing Your Comic...`;

    try {
      const res = await fetch('/api/export-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comic_data: state.currentComic })
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'PDF generation error');
      }

      state.pdfUrl = data.pdf_url;

      if (openPreviewTab) {
        window.open(data.pdf_url, '_blank');
      } else {
        triggerFileDownload(data.pdf_url);
      }

      // Show Export Success Modal
      if (elements.successComicTitle) {
        elements.successComicTitle.textContent = state.currentComic.title;
      }
      elements.successOverlay.classList.add('active');

      // Fire celebratory confetti!
      if (window.fireComicConfetti) {
        window.fireComicConfetti();
      }

    } catch (err) {
      showToast(`Export failed: ${err.message}`, 'error');
    } finally {
      state.isExportingPdf = false;
      elements.downloadPdfBtn.disabled = false;
      elements.downloadPdfBtn.innerHTML = originalText;
    }
  }

  function triggerFileDownload(url) {
    const a = document.createElement('a');
    a.href = url;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // ==========================================
  // SAMPLE COMICS GALLERY
  // ==========================================
  function setupSampleComicCards() {
    document.querySelectorAll('.btn-view-sample').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const sampleId = btn.getAttribute('data-sample-id');
        btn.disabled = true;
        btn.textContent = 'Loading...';

        try {
          const res = await fetch(`/api/sample-comics/${sampleId}`);
          const data = await res.json();
          if (data && data.success && data.comic) {
            state.currentComic = data.comic;
            renderComicPreview(data.comic);

            // Populate form with this sample's settings
            elements.promptInput.value = data.comic.summary || data.comic.title;
            elements.characterInput.value = data.comic.character;
            elements.settingSelect.value = data.comic.setting;
            selectTone(data.comic.tone);
            selectArtStyle(data.comic.art_style);
            selectPanelsCount(data.comic.panels ? data.comic.panels.length : 5);

            // Show preview
            elements.previewSection.classList.add('active');
            elements.previewSection.scrollIntoView({ behavior: 'smooth' });

            showToast(`Loaded sample "${data.comic.title}"!`, 'success');
          }
        } catch (err) {
          showToast('Could not load sample comic.', 'error');
        } finally {
          btn.disabled = false;
          btn.textContent = 'View Comic';
        }
      });
    });
  }

  // ==========================================
  // TOAST NOTIFICATIONS
  // ==========================================
  function showToast(message, type = 'info') {
    if (!elements.toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'ℹ️';
    if (type === 'success') icon = '✓';
    if (type === 'error') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 300);
    }, 4000);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Self execute
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
