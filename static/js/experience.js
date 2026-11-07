(() => {
    const config = document.getElementById('experience-config');
    const loadingState = document.getElementById('loading');
    const errorState = document.getElementById('error');
    const emptyState = document.getElementById('empty');
    const gridContainer = document.getElementById('grid');
    const searchForm = document.getElementById('experience-search-form');
    const searchInput = document.getElementById('search-input');
    const experienceForm = document.getElementById('experience-form');
    const experienceFormModal = document.getElementById('experience-form-modal');
    const experienceFormTitle = document.querySelector('[data-experience-form-title]');
    const experienceFormSubmit = document.querySelector('[data-experience-form-submit]');
    const experienceAddButton = document.querySelector('[data-experience-add-button]');
    const experienceCardTemplate = document.getElementById('experience-card-template');

    if (!config || !loadingState || !errorState || !emptyState || !gridContainer || !searchForm || !searchInput || !experienceCardTemplate) {
        console.error('Experience page is missing required elements.');
        return;
    }

    const experienceEndpoints = {
        list: config.dataset.experienceEndpoint,
        detail: config.dataset.detailUrlTemplate,
        star: config.dataset.starUrlTemplate,
    };
    const formFields = ['title', 'description', 'category', 'thumbnail', 'started_at', 'ended_at'];
    const searchDebounceDelay = 300;
    const experienceIdPlaceholder = '00000000-0000-0000-0000-000000000000';
    let experiencesAbortController;
    let searchDebounceTimer;

    function displayPageSection({ showLoading = false, showError = false, showEmpty = false, showGrid = false }) {
        loadingState.classList.toggle('hide', !showLoading);
        errorState.classList.toggle('hide', !showError);
        emptyState.classList.toggle('hide', !showEmpty);
        gridContainer.classList.toggle('hide', !showGrid);
    }

    function experienceUrl(template, experienceId) {
        return template.replace(experienceIdPlaceholder, encodeURIComponent(experienceId));
    }

    function buildExperienceCardElement(experience) {
        const experienceId = experience.id;
        const card = experienceCardTemplate.content.firstElementChild.cloneNode(true);
        const image = card.querySelector('[data-experience-thumbnail]');
        const name = experience.title || '';
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
        card.querySelector('[data-experience-category]').textContent = experience.category_display || '';
        const formatDate = value => new Date(`${value}T00:00:00`).toLocaleDateString('id-ID');
        card.querySelector('[data-experience-period]').textContent =
            `${formatDate(experience.started_at)} - ${experience.ended_at
                ? `${formatDate(experience.ended_at)} (Selesai)` : 'Sedang berlangsung'}`;

        const starForm = card.querySelector('[data-experience-star-form]');
        const starButton = card.querySelector('[data-experience-star-button]');
        if (starForm && starButton) {
            starForm.action = experienceUrl(experienceEndpoints.star, experienceId);
            updateStarState(starForm, experience);
        } else {
            card.querySelector('[data-experience-star-count]').textContent = String(experience.star_count ?? 0);
        }

        const editButton = card.querySelector('[data-experience-edit-button]');
        if (editButton) {
            editButton.dataset.experienceId = experienceId;
            editButton.dataset.experienceFields = JSON.stringify(
                Object.fromEntries(formFields.map(field => [field, experience[field] ?? ''])),
            );
            editButton.setAttribute('aria-label', `Edit ${name}`);
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
                experienceUrl(experienceEndpoints.detail, experienceId);
        }

        return card;
    }

    async function fetchExperiences(searchQuery = '') {
        experiencesAbortController?.abort();
        experiencesAbortController = new AbortController();

        try {
            displayPageSection({ showLoading: true });
            const url = new URL(experienceEndpoints.list, window.location.href);
            if (searchQuery) {
                url.searchParams.set('title', searchQuery);
            }

            const response = await fetch(url, {
                headers: { Accept: 'application/json' },
                signal: experiencesAbortController.signal,
            });
            if (!response.ok) {
                throw new Error(`Failed to fetch experiences (status ${response.status}).`);
            }

            const experienceData = await response.json();
            if (!Array.isArray(experienceData)) {
                throw new Error('Experience API returned an invalid response.');
            }

            gridContainer.replaceChildren(...experienceData.map(buildExperienceCardElement));
            if (experienceData.length === 0) {
                displayPageSection({ showEmpty: true });
                return;
            }

            displayPageSection({ showGrid: true });
        } catch (error) {
            if (error.name === 'AbortError') {
                return;
            }
            console.error('Error loading experiences:', error);
            displayPageSection({ showError: true });
        }
    }

    function searchExperiences() {
        fetchExperiences(searchInput.value.trim());
    }

    searchInput.addEventListener('input', () => {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(searchExperiences, searchDebounceDelay);
    });

    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        clearTimeout(searchDebounceTimer);
        searchExperiences();
    });

    let editingExperienceId = null;

    function prepareExperienceFormForCreate() {
        if (!experienceForm) {
            return;
        }
        editingExperienceId = null;
        experienceForm.reset();
        experienceFormTitle.textContent = 'Tambah Experience Baru';
        experienceFormSubmit.textContent = 'Tambah Experience';
    }

    experienceAddButton?.addEventListener('click', prepareExperienceFormForCreate);

    gridContainer.addEventListener('click', (event) => {
        const editButton = event.target.closest('[data-experience-edit-button]');
        if (!editButton || !experienceForm || !experienceFormModal) {
            return;
        }

        editingExperienceId = editButton.dataset.experienceId;
        const values = JSON.parse(editButton.dataset.experienceFields);
        formFields.forEach(field => {
            experienceForm.elements.namedItem(field).value = values[field];
        });
        experienceFormTitle.textContent = 'Edit Experience';
        experienceFormSubmit.textContent = 'Simpan Perubahan';
        experienceFormModal.showPopover();
    });

    function getCookie(name) {
        const prefix = `${name}=`;
        const cookie = document.cookie.split(';').map(value => value.trim())
            .find(value => value.startsWith(prefix));
        return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
    }

    function apiErrorMessage(data, status) {
        function messages(value) {
            if (typeof value === 'string') return [value];
            if (value && typeof value === 'object') return Object.values(value).flatMap(messages);
            return [];
        }
        return messages(data).join(' ') || `Terjadi kesalahan (status ${status}).`;
    }

    async function writeExperience(url, method, payload, form) {
        const response = await fetch(url, {
            method,
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': form?.querySelector('[name="csrfmiddlewaretoken"]')?.value
                    || getCookie('csrftoken') || '',
            },
            body: payload === undefined ? undefined : JSON.stringify(payload),
        });
        if (response.ok && response.status === 204) return null;
        if (!response.headers.get('content-type')?.includes('application/json')) {
            throw new Error(response.redirected
                ? 'Sesi login berakhir. Silakan login kembali.'
                : 'Server mengembalikan respons yang tidak valid.');
        }
        const data = await response.json();
        if (!response.ok) throw new Error(apiErrorMessage(data, response.status));
        return data;
    }

    function updateStarState(form, experience) {
        if (typeof experience.is_starred !== 'boolean'
            || !Number.isInteger(experience.star_count)
            || typeof experience.starred_by_names !== 'string') {
            throw new Error('Server mengembalikan status star yang tidak valid.');
        }
        const button = form.querySelector('[data-experience-star-button]');
        button.classList.toggle('is-starred', experience.is_starred);
        button.title = experience.star_count > 0
            ? `Dibintangi oleh ${experience.starred_by_names}`
            : 'Jadilah yang pertama memberi star';
        form.querySelector('[data-experience-star-label]').textContent = experience.is_starred ? 'Unstar' : 'Star';
        form.querySelector('[data-experience-star-count]').textContent = String(experience.star_count);
    }

    gridContainer.addEventListener('submit', async (event) => {
        const form = event.target.closest('[data-experience-star-form], [data-experience-delete-form]');
        if (!form) return;
        event.preventDefault();
        const button = form.querySelector('button[type="submit"]');
        if (button.disabled) return;
        button.disabled = true;
        const isStar = form.matches('[data-experience-star-form]');
        try {
            const result = await writeExperience(form.action, isStar ? 'POST' : 'DELETE', undefined, form);
            if (isStar) {
                updateStarState(form, result);
            } else {
                form.closest('[data-experience-delete-modal]').hidePopover();
                showToast('Berhasil', 'Experience berhasil dihapus!', 'success');
                await fetchExperiences(searchInput.value.trim());
            }
        } catch (error) {
            console.error('Error updating experience:', error);
            showToast(isStar ? 'Gagal memperbarui star' : 'Gagal menghapus experience',
                error.message || 'Tidak dapat terhubung ke server. Silakan coba lagi.', 'error');
        } finally {
            button.disabled = false;
        }
    });

    if (experienceForm) {
        experienceForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const submitButton = experienceForm.querySelector('button[type="submit"]');
            if (!submitButton) {
                console.error('Experience form is missing its submit button.');
                return;
            }
            if (submitButton.disabled) return;
            submitButton.disabled = true;

            const isEditing = Boolean(editingExperienceId);
            const endpoint = isEditing
                ? experienceUrl(experienceEndpoints.detail, editingExperienceId)
                : experienceEndpoints.list;

            try {
                const fields = new FormData(experienceForm);
                const payload = Object.fromEntries(
                    formFields.map(name => [name, name === 'ended_at' ? fields.get(name) || null : fields.get(name)]),
                );
                await writeExperience(endpoint, isEditing ? 'PATCH' : 'POST', payload, experienceForm);
                experienceForm.reset();
                experienceFormModal?.hidePopover();
                editingExperienceId = null;
                showToast(
                    'Berhasil',
                    isEditing ? 'Experience berhasil diperbarui!' : 'Experience baru berhasil ditambahkan!',
                    'success',
                );
                await fetchExperiences(searchInput.value.trim());
            } catch (error) {
                console.error(isEditing ? 'Error updating experience:' : 'Error adding experience:', error);
                showToast(
                    isEditing ? 'Gagal mengubah experience' : 'Gagal menambahkan experience',
                    error.message || 'Tidak dapat terhubung ke server. Silakan coba lagi.',
                    'error',
                );
            } finally {
                submitButton.disabled = false;
            }
        });
    }

    fetchExperiences(searchInput.value.trim());
})();
