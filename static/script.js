document.addEventListener('DOMContentLoaded', () => {
    // --- ELEMENTOS DEL DOM ---
    const initialView = document.getElementById('initial-view');
    const resultsView = document.getElementById('results-view');
    const textarea = document.getElementById('prompt-input');
    const sendButton = document.getElementById('send-button');
    const userPromptDisplay = document.getElementById('user-prompt-display');
    const keywordsList = document.getElementById('keywords-list');
    const meterCircle = document.getElementById('meter-circle');
    const meterValue = document.getElementById('meter-value');
    const infoColumn = document.getElementById('info-column');
    const workflowTracker = document.getElementById('workflow-tracker');

    let ws;

    const WORKFLOW_STEPS = [
        { name: "keywords_extraction", label: "Extracción de Keywords" },
        { name: "brave_search", label: "Búsqueda de Información" },
        { name: "normalize_results", label: "Normalización de Datos" },
        { name: "inference_items", label: "Análisis de Inferencia" },
        { name: "confidence_items", label: "Cálculo de Confianza" },
        { name: "context_items", label: "Análisis de Contexto" },
        { name: "veracity_score", label: "Puntuación de Veracidad" }
    ];

    // --- FUNCIONES DE RENDERIZADO ---

    const renderWorkflow = () => {
        workflowTracker.innerHTML = '';
        WORKFLOW_STEPS.forEach(step => {
            const stepDiv = document.createElement('div');
            stepDiv.className = 'workflow-step pending';
            stepDiv.id = `wf-${step.name}`;
            stepDiv.innerHTML = `
                <div class="step-icon"><i class="bi bi-circle"></i></div>
                <span class="step-name">${step.label}</span>
            `;
            workflowTracker.appendChild(stepDiv);
        });
    };

    const updateWorkflow = (stepName) => {
        let activeStepFound = false;
        WORKFLOW_STEPS.forEach(step => {
            const stepEl = document.getElementById(`wf-${step.name}`);
            if (!stepEl) return;

            if (activeStepFound) {
                 stepEl.className = 'workflow-step pending';
                 stepEl.querySelector('.step-icon').innerHTML = `<i class="bi bi-circle"></i>`;
            } else if (step.name === stepName) {
                stepEl.className = 'workflow-step active';
                stepEl.querySelector('.step-icon').innerHTML = `<div class="spinner-tiny"></div>`;
                activeStepFound = true;
            } else {
                 stepEl.className = 'workflow-step completed';
                 stepEl.querySelector('.step-icon').innerHTML = `<i class="bi bi-check-circle-fill"></i>`;
            }
        });
    };
    
    const renderKeywords = (data) => {
        keywordsList.innerHTML = '';
        if (!data.keywords || !Array.isArray(data.keywords)) return;
        data.keywords.forEach(term => {
            const tag = document.createElement('span');
            tag.className = 'keyword-tag';
            tag.textContent = term;
            keywordsList.appendChild(tag);
        });
    };

    const renderPlaceholders = (data) => {
        infoColumn.innerHTML = ''; // Limpiar
        if (!data.items || !Array.isArray(data.items)) return;
        data.items.forEach((item, index) => {
            const placeholderDiv = document.createElement('div');
            placeholderDiv.className = 'item-placeholder';
            // Usamos el índice como ID temporal, lo reemplazaremos por uno más robusto si es posible
            placeholderDiv.id = `item-${index}`; 
            placeholderDiv.innerHTML = `
                <div class="ph-title"></div>
                <div class="ph-summary w-90"></div>
                <div class="ph-summary w-60"></div>
            `;
            infoColumn.appendChild(placeholderDiv);
        });
    };

    const updateCard = (index, itemData) => {
        const card = document.getElementById(`item-${index}`);
        if (!card) return;

        // Reemplazamos el placeholder con la tarjeta real
        card.className = 'info-item';
        card.innerHTML = `
            <div class="item-header">
                <h4 class="item-title"><a href="${itemData.url}" target="_blank" rel="noopener noreferrer">${itemData.title}</a></h4>
                <span class="item-source">${itemData.meta_data.source}</span>
            </div>
            <p class="item-summary">${itemData.resumen}</p>
            <div class="item-metrics">
                <div class="metric metric-inference">
                    <span class="metric-label">Inference</span>
                    <span class="metric-value">${itemData.inference ? `${(itemData.inference * 100).toFixed(0)}%` : '<div class="metric-placeholder"><div class="spinner-tiny"></div></div>'}</span>
                </div>
                <div class="metric metric-confidence">
                    <span class="metric-label">Confidence</span>
                    <span class="metric-value">${itemData.confidence ? `${(itemData.confidence * 100).toFixed(0)}%` : '<div class="metric-placeholder"><div class="spinner-tiny"></div></div>'}</span>
                </div>
                <div class="metric metric-context">
                    <span class="metric-label">Context</span>
                    <span class="metric-value">${itemData.context ? `${(itemData.context * 100).toFixed(0)}%` : '<div class="metric-placeholder"><div class="spinner-tiny"></div></div>'}</span>
                </div>
                <div class="metric score-metric">
                    <span class="metric-label">Score</span>
                    <span class="metric-value">${itemData.score ? `${(itemData.score * 100).toFixed(0)}%` : '<div class="metric-placeholder"><div class="spinner-tiny"></div></div>'}</span>
                </div>
            </div>
        `;
    };

    const updateAllCards = (data) => {
        if (!data.items || !Array.isArray(data.items)) return;
        data.items.forEach((item, index) => {
            updateCard(index, item);
        });
    };

    const updateMeter = (veracity) => {
        const veracityPercent = Math.round(veracity);
        meterValue.textContent = `${veracityPercent}%`;
        meterCircle.style.setProperty('--value', veracityPercent);
    };

    // --- LÓGICA PRINCIPAL ---

    const startAnalysis = () => {
        const promptText = textarea.value.trim();
        if (!promptText) return;

        userPromptDisplay.textContent = promptText;
        initialView.classList.replace('view-active', 'view-hidden');
        resultsView.classList.replace('view-hidden', 'view-active');
        workflowTracker.classList.remove('hidden');
        renderWorkflow();
        
        ws = new WebSocket("ws://localhost:8001/agent/ltv/ws");

        ws.onopen = () => {
            ws.send(JSON.stringify({ text: promptText }));
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log("Mensaje recibido:", message.step_name, message);

            // Actualizar el flujo de trabajo
            if(message.step_name) {
                updateWorkflow(message.step_name);
            }

            // Manejar la lógica de cada paso
            if (message.step_name === 'keywords_extraction_completed') {
                renderKeywords(message.data);
            } else if (message.step_name === 'brave_search_completed') {
                renderPlaceholders(message.data);
                // Ahora actualizamos las tarjetas con la info inicial que tenemos
                updateAllCards(message.data); 
            } else if (message.step_name && message.step_name.endsWith('_completed')) {
                // Para los demás pasos, actualizamos todas las tarjetas
                updateAllCards(message.data);
            }

            // Manejo del resultado final
            if (message.status === 'final_result') {
                updateMeter(message.data.overall_veracity);
                updateAllCards(message.data); // Última actualización con todos los scores
                
                // Ocultar el tracker después de un momento
                setTimeout(() => {
                    workflowTracker.classList.add('hidden');
                }, 1500);
            }
        };

        ws.onerror = (error) => console.error("Error en WebSocket:", error);
        ws.onclose = () => console.log("WebSocket desconectado.");
    };

    sendButton.addEventListener('click', startAnalysis);
    textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            startAnalysis();
        }
    });
});