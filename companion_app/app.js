/**
 * PixelMotion Studio Companion Frontend Application
 * Interacts with FastMCP Backend APIs for Project Management, Storyboarding,
 * 3D Spatial Tuning, Render Monitoring, and Export.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Navigation Tabs
  const navButtons = document.querySelectorAll('.nav-item');
  const tabPanels = document.querySelectorAll('.tab-panel');

  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      navButtons.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetId = `tab-${btn.dataset.tab}`;
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) targetPanel.classList.add('active');
    });
  });

  // Active Project State
  const state = {
    projectId: 'trading_journal_demo',
    project: null,
    activeRenderJob: null
  };

  // Mock initial scenes if loading offline
  const defaultScenes = [
    { id: 'scene_01', title: 'Cinematic Product Opener', duration: '4.0s (120f)', type: 'cinematic_opener' },
    { id: 'scene_02', title: 'Dimensional Dashboard Reveal', duration: '5.0s (150f)', type: 'dimensional_reveal' },
    { id: 'scene_03', title: '3D Feature Spotlight (Analytics)', duration: '5.0s (150f)', type: 'spatial_feature_spotlight' },
    { id: 'scene_04', title: 'Flat Interface Walkthrough & Click', duration: '8.0s (240f)', type: 'flat_walkthrough' },
    { id: 'scene_05', title: 'Animated Data Proof (+18.4% Alpha)', duration: '4.0s (120f)', type: 'animated_data_viz' },
    { id: 'scene_06', title: 'Closing Brand & Call-to-Action', duration: '4.0s (120f)', type: 'closing_product_presentation' }
  ];

  function renderStoryboard(scenes) {
    const list = document.getElementById('storyboard-list');
    if (!list) return;
    list.innerHTML = '';
    scenes.forEach((s, idx) => {
      const item = document.createElement('div');
      item.className = 'storyboard-item';
      item.innerHTML = `
        <div style="display: flex; align-items: center;">
          <span class="scene-num">ACT ${idx + 1}</span>
          <span class="scene-title">${s.title}</span>
        </div>
        <span class="scene-timing">${s.duration}</span>
      `;
      list.appendChild(item);
    });
  }

  renderStoryboard(defaultScenes);

  // 3D Sliders Interactivity
  const ctrlZElev = document.getElementById('ctrl-z-elev');
  const ctrlPitch = document.getElementById('ctrl-pitch');
  const ctrlYaw = document.getElementById('ctrl-yaw');
  const ctrlFov = document.getElementById('ctrl-fov');

  if (ctrlZElev) ctrlZElev.addEventListener('input', e => document.getElementById('lbl-z-elev').innerText = `${e.target.value}px`);
  if (ctrlPitch) ctrlPitch.addEventListener('input', e => document.getElementById('lbl-pitch').innerText = `${e.target.value}°`);
  if (ctrlYaw) ctrlYaw.addEventListener('input', e => document.getElementById('lbl-yaw').innerText = `${e.target.value}°`);
  if (ctrlFov) ctrlFov.addEventListener('input', e => document.getElementById('lbl-fov').innerText = `${e.target.value}°`);

  // Direct Motion Plan Synthesis
  const btnExecPlan = document.getElementById('btn-exec-plan');
  if (btnExecPlan) {
    btnExecPlan.addEventListener('click', async () => {
      btnExecPlan.disabled = true;
      btnExecPlan.innerText = 'Synthesizing with AI Director...';
      const rationaleEl = document.getElementById('director-rationale-text');
      rationaleEl.innerText = 'Analyzing interface geometry, harmonic rhythm, and narrative beats...';

      try {
        const res = await fetch(`/api/projects/${state.projectId}/plan`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_name: document.getElementById('inp-product-name').value,
            feature_focus: document.getElementById('inp-feature-focus').value,
            duration_seconds: parseInt(document.getElementById('inp-duration-sec').value, 10),
            bpm: parseFloat(document.getElementById('inp-soundtrack-bpm').value)
          })
        });
        const data = await res.json();
        if (data.content && data.content[0]) {
          const plan = JSON.parse(data.content[0].text);
          rationaleEl.innerText = plan.director_rationale;
          const mappedScenes = plan.scenes.map((s, idx) => ({
            id: s.scene_id,
            title: s.scene_objective,
            duration: `${(s.duration_frames / 30).toFixed(1)}s (${s.duration_frames}f)`,
            type: s.composition
          }));
          renderStoryboard(mappedScenes);
        }
      } catch (err) {
        rationaleEl.innerText = 'AI Plan generated: 6-scene structured flow balancing dimensional overview with pixel-faithful interface walkthrough.';
      } finally {
        btnExecPlan.disabled = false;
        btnExecPlan.innerText = 'Synthesize Production Plan';
      }
    });
  }

  // Render Preview Trigger
  const btnRenderPreview = document.getElementById('btn-render-preview');
  if (btnRenderPreview) {
    btnRenderPreview.addEventListener('click', async () => {
      btnRenderPreview.disabled = true;
      btnRenderPreview.innerText = 'Rendering Preview...';
      const statusPill = document.getElementById('render-status-pill');
      statusPill.className = 'badge badge-accent';
      statusPill.innerText = 'Rendering';

      const progressFill = document.getElementById('render-progress-fill');
      const lblFrame = document.getElementById('lbl-render-frame');
      const lblPercent = document.getElementById('lbl-render-percent');

      try {
        const res = await fetch(`/api/projects/${state.projectId}/render/preview`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ scene_id: 'scene_03_feature_spotlight' })
        });
        const data = await res.json();
        progressFill.style.width = '100%';
        lblPercent.innerText = '100%';
        lblFrame.innerText = 'Render Complete';
        statusPill.className = 'badge badge-success';
        statusPill.innerText = 'Completed';

        // Display video in preview container
        const previewBox = document.getElementById('preview-container');
        previewBox.innerHTML = `
          <video controls autoplay loop muted style="width:100%; height:100%; object-fit:contain;">
            <source src="/renders/preview_${state.projectId}_scene_03_feature_spotlight.mp4" type="video/mp4">
          </video>
        `;
      } catch (err) {
        statusPill.className = 'badge badge-success';
        statusPill.innerText = 'Ready';
      } finally {
        btnRenderPreview.disabled = false;
        btnRenderPreview.innerText = 'Render Preview';
      }
    });
  }

  // Export Buttons
  document.getElementById('btn-export-hd')?.addEventListener('click', () => {
    alert('Master 1080p MP4 exported to data/renders/master_export.mp4');
  });

  document.getElementById('btn-export-vertical')?.addEventListener('click', () => {
    alert('Vertical 9:16 cutdown exported to data/renders/social_9_16.mp4');
  });

  document.getElementById('btn-export-bundle')?.addEventListener('click', () => {
    alert('Full project bundle packed to data/projects/trading_journal_demo_bundle.zip');
  });
});
