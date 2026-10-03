(() => {
    const config = document.getElementById('experience-config');
    const loadingState = document.getElementById('loading');
    const errorState = document.getElementById('error');
    const emptyState = document.getElementById('empty');
    const gridContainer = document.getElementById('grid');
    const searchForm = document.getElementById('experience-search-form');
    const searchInput = document.getElementById('search-input');
    const experienceCardTemplate = document.getElementById('experience-card-template');

    if (!config || !loadingState || !errorState || !emptyState || !gridContainer || !searchForm || !searchInput || !experienceCardTemplate) {
        console.error('Experience page is missing required elements.');
        return;
    }

    const experienceEndpoints = {
        list: config.dataset.experienceEndpoint,
        edit: config.dataset.editUrlTemplate,
        delete: config.dataset.deleteUrlTemplate,
        star: config.dataset.starUrlTemplate,
    };
    const searchDebounceDelay = 300;
    let searchDebounceTimer;
    const experienceIdPlaceholder = '00000000-0000-0000-0000-000000000000';
    let experienceAbortController;

    function displayPageSection({ showLoading = false, showError = false, showEmpty = false, showGrid = false }) {
        loadingState.classList.toggle('hide', !showLoading);
        errorState.classList.toggle('hide', !showError);
        emptyState.classList.toggle('hide', !showEmpty);
        gridContainer.classList.toggle('hide', !showGrid);
    }

    function experienceUrl(template, experienceId) {
        return template.replace(experienceIdPlaceholder, encodeURIComponent(experienceId));
    }

    function buildExperienceCardElement(item) {
        const experience = item.fields;
        const experienceId = item.pk;
        const card = experienceCardTemplate.content.firstElementChild.cloneNode(true);
        const image = card.querySelector('[data-experience-thumbnail]');
        const name = experience.title || '';
        const category = experience.category_display || '';
        const modalId = `delete-experience-${experienceId}`;
        const modalTitleId = `delete-experience-title-${experienceId}`;

        image.hidden = !experience.thumbnail;
        image.classList.toggle('hide', !experience.thumbnail);
        if (experience.thumbnail) {
            image.src = experience.thumbnail;
            image.alt = `Gambar ${name}`;
        }
        card.querySelector('[data-experience-title]').textContent = name;
        card.querySelector('[data-experience-description]').textContent = experience.description || '';
        card.querySelector('[data-experience-category]').textContent = category;

        const starForm = card.querySelector('[data-experience-star-form]');
        const starButton = card.querySelector('[data-experience-star-button]');
        starForm.action = experienceUrl(experienceEndpoints.star, experienceId);
        starButton.classList.toggle('is-starred', Boolean(experience.is_starred));
        starButton.title = experience.star_count > 0
            ? `Dibintangi oleh ${experience.starred_by_names || ''}`
            : 'Jadilah yang pertama memberi star';
        card.querySelector('[data-experience-star-label]').textContent = experience.is_starred ? 'Unstar' : 'Star';
        card.querySelector('[data-experience-star-count]').textContent = String(experience.star_count ?? 0);

        const editLink = card.querySelector('[data-experience-edit-link]');
        if (editLink) {
            editLink.href = experienceUrl(experienceEndpoints.edit, experienceId);
            editLink.setAttribute('aria-label', `Edit ${name}`);
        }

        const deleteTrigger = card.querySelector('[data-experience-delete-trigger]');
        const deleteModal = card.querySelector('[data-experience-delete-modal]');
        if (deleteTrigger && deleteModal) {
            deleteModal.id = modalId;
            deleteModal.setAttribute('aria-labelledby', modalTitleId);
            deleteTrigger.setAttribute('popovertarget', modalId);
            deleteTrigger.setAttribute('aria-label', `Hapus ${name}`);
            deleteModal.querySelector('[data-experience-delete-title]').id = modalTitleId;
            deleteModal.querySelector('[data-experience-delete-name]').textContent = name;
            deleteModal.querySelectorAll('[popovertargetaction="hide"]').forEach((button) => {
                button.setAttribute('popovertarget', modalId);
            });
            deleteModal.querySelector('[data-experience-delete-form]').action =
                experienceUrl(experienceEndpoints.delete, experienceId);
        }

        return card;
    }

    async function fetchExperience(searchQuery = '') {
        experienceAbortController?.abort();
        experienceAbortController = new AbortController();

        try {
            displayPageSection({ showLoading: true });
            const url = new URL(experienceEndpoints.list, window.location.href);
            if (searchQuery) {
                url.searchParams.set('title', searchQuery);
            }

            const response = await fetch(url, {
                headers: { Accept: 'application/json' },
                signal: experienceAbortController.signal,
            });
            if (!response.ok) {
                throw new Error(`Failed to fetch experience (status ${response.status}).`);
            }

            const experienceData = await response.json();
            if (!Array.isArray(experienceData)) {
                throw new Error('experience API returned an invalid response.');
            }

            gridContainer.replaceChildren();
            if (experienceData.length === 0) {
                displayPageSection({ showEmpty: true });
                return;
            }

            experienceData.forEach((item) => {
                gridContainer.appendChild(buildExperienceCardElement(item));
            });
            displayPageSection({ showGrid: true });
        } catch (error) {
            if (error.name === 'AbortError') {
                return;
            }
            console.error('Error loading experience:', error);
            displayPageSection({ showError: true });
        }
    }

    function searchExperience() {
        fetchExperience(searchInput.value.trim());
    }

    searchInput.addEventListener('input', () => {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(searchExperience, searchDebounceDelay);
    });

    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        clearTimeout(searchDebounceTimer);
        searchExperience();
    });

    fetchExperience(searchInput.value.trim());
})();