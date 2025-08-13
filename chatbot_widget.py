# chatbot_overlay.py
import json
import streamlit as st
import streamlit.components.v1 as components

def render_chatbot_overlay(title: str = "ECCB Assistant", corner: str = "right") -> None:
    side_prop = "right" if corner not in {"left", "right"} or corner == "right" else "left"

    HTML = r"""
    <script>
    (function(){
      const TITLE   = __TITLE__;
      const SIDE    = __SIDE__;
      const APIBASE = __APIBASE__; // e.g. "http://localhost:7861/chatapi" or "" to skip

      const HOST_ID = "eccb-global-chat-host";
      if (window.parent.document.getElementById(HOST_ID)) return;

      // host in parent (true overlay)
      const host = window.parent.document.createElement('div');
      host.id = HOST_ID;
      host.style.all='initial'; host.style.position='fixed';
      host.style.bottom='18px'; host.style[ SIDE ]='18px';
      host.style.zIndex='2147483647';
      window.parent.document.body.appendChild(host);

      const shadow = host.attachShadow({mode:'open'});

      const css = `
        :host{all:initial}
        .eccb-chatbot{width:340px;border-radius:12px;overflow:hidden;font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:#fff;box-shadow:0 12px 36px rgba(0,0,0,.22)}
        .cb-header{background:#f4f5f7;padding:10px 12px;font-weight:700;display:flex;align-items:center;justify-content:space-between;cursor:pointer;user-select:none;border-bottom:1px solid #e6e8eb}
        .cb-title{color:#c1126b}
        .cb-body{height:380px;display:flex;flex-direction:column;background:#fff}
        .cb-messages{flex:1;overflow-y:auto;padding:12px;background:#f8fafc}
        .msg{max-width:85%;padding:10px 12px;margin:6px 0;border-radius:12px;line-height:1.25;font-size:14px;box-shadow:0 1px 0 rgba(0,0,0,.04)}
        .msg.user{background:#eef2ff;margin-left:auto;border:1px solid #e0e7ff}
        .msg.bot{background:#f1f5f9;margin-right:auto;border:1px solid #e2e8f0}
        .cb-input{display:flex;gap:8px;padding:12px;border-top:1px solid #e2e8f0;background:#fff}
        .cb-input input{flex:1;padding:10px 12px;border:1px solid #d0d7de;border-radius:10px;outline:none}
        .cb-input button{padding:10px 14px;border:0;border-radius:10px;cursor:pointer;font-weight:600;color:#fff;background:#c1126b}

        /* Onboarding panel (asks name/country/email) */
        .pane{padding:12px}
        .pane h4{margin:0 0 8px 0}
        .row{display:flex;gap:8px;margin:6px 0}
        .row input, .row select{flex:1;padding:10px;border:1px solid #d0d7de;border-radius:10px;outline:none}
        .row button{padding:10px 14px;border:0;border-radius:10px;cursor:pointer;font-weight:600;color:#fff;background:#16a34a}
        .help{font-size:12px;color:#64748b}

        .hidden{display:none}
      `;

      const html = `
        <div id="eccb-chatbot" class="eccb-chatbot">
          <div class="cb-header" id="eccb-toggle">
            <div class="cb-title">${TITLE}</div>
            <div id="eccb-minmax" aria-hidden="true">–</div>
          </div>

          <div class="cb-body">
            <div id="onboard" class="pane">
              <h4>Let's get you set up</h4>
              <div class="row"><input id="ob-name" type="text" placeholder="Your name"></div>
              <div class="row">
                <select id="ob-country">
                  <option value="">Select country</option>
                  <option>Anguilla</option>
                  <option>Antigua & Barbuda</option>
                  <option>Dominica</option>
                  <option>Grenada</option>
                  <option>Montserrat</option>
                  <option>St. Kitts & Nevis</option>
                  <option>St. Lucia</option>
                  <option>St. Vincent & the Grenadines</option>
                  <option>Other</option>
                </select>
                <input id="ob-email" type="email" placeholder="Email">
              </div>
              <div class="row"><button id="ob-save">Continue</button></div>
              <div class="help">We’ll remember you and your chat on this device. If the green server is enabled, we also save it on the server to resume anywhere.</div>
            </div>

            <div id="eccb-messages" class="cb-messages hidden" aria-live="polite"></div>

            <div class="cb-input hidden" id="eccb-inputbar">
              <input id="eccb-input" type="text" placeholder="Type a message..." autocomplete="off" />
              <button id="eccb-send">Send</button>
            </div>
          </div>
        </div>
      `;

      const style = document.createElement('style'); style.textContent = css;
      const wrap  = document.createElement('div');  wrap.innerHTML = html;
      shadow.appendChild(style); shadow.appendChild(wrap);

      // --- state + helpers ---
      const LS_PROFILE = 'eccb_user_profile_v1';
      const LS_CHAT    = 'eccb_chat_history_v2'; // per user id
      const LS_MIN     = 'eccb_chat_min';

      const root  = wrap.querySelector('#eccb-chatbot');
      const pane  = wrap.querySelector('#onboard');
      const msgEl = wrap.querySelector('#eccb-messages');
      const barEl = wrap.querySelector('#eccb-inputbar');
      const input = wrap.querySelector('#eccb-input');
      const sendB = wrap.querySelector('#eccb-send');
      const toggle= wrap.querySelector('#eccb-toggle');
      const icon  = wrap.querySelector('#eccb-minmax');

      function uuid(){return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,c=>{const r=Math.random()*16|0,v=c==='x'?r:(r&0x3|0x8);return v.toString(16)})}
      function validEmail(s){return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s)}
      function profileKey(){ const p = getProfile(); return p ? ('eccb_chat_'+p.uid) : LS_CHAT; }

      function getProfile(){
        try{ return JSON.parse(localStorage.getItem(LS_PROFILE)) || null }catch{ return null }
      }
      function saveProfile(p){
        localStorage.setItem(LS_PROFILE, JSON.stringify(p));
      }

      function loadHistory(){
        try{ return JSON.parse(localStorage.getItem(profileKey())) || [] }catch{ return [] }
      }
      function saveHistory(items){
        localStorage.setItem(profileKey(), JSON.stringify(items));
      }

      function render(messages){
        msgEl.innerHTML = '';
        messages.forEach(m=>{
          const div = document.createElement('div');
          div.className = 'msg ' + (m.role==='user'?'user':'bot');
          div.textContent = m.text;
          msgEl.appendChild(div);
        });
        msgEl.scrollTop = msgEl.scrollHeight;
      }

      function setMinimized(min){
        if(min){ root.classList.add('min'); icon.textContent='+'; }
        else   { root.classList.remove('min'); icon.textContent='–'; }
        localStorage.setItem(LS_MIN, min ? '1':'0');
      }

      // --- server calls (optional) ---
      async function postJSON(url, body){
        if(!APIBASE) return null; // no server configured
        try{
          const res = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
          if(!res.ok) return null;
          return await res.json();
        }catch(e){ return null; }
      }

      async function registerOnServer(p){ return postJSON(APIBASE + '/register', p); }
      async function appendLogOnServer(uid, entry){ return postJSON(APIBASE + '/log', { uid, entry }); }
      async function loadHistoryFromServer(uid){
        if(!APIBASE) return null;
        try{
          const res = await fetch(APIBASE + '/history?uid=' + encodeURIComponent(uid));
          if(!res.ok) return null;
          return await res.json();
        }catch(e){ return null; }
      }

      // --- simple intent router (demo) ---
      function numsIn(t){ return (t.toLowerCase().match(/-?\d+(\.\d+)?/g)||[]).map(Number) }
      function greet(name){ return name ? `Hi ${name}! How can I help today?` : `Hi! How can I help today?` }

      async function botReply(text){
        // add your own branching here. For now just echo with slight smarts.
        const p = getProfile();
        if(/^hi|hello|hey\b/i.test(text)) return greet(p?.name);
        const ns = numsIn(text);
        if(/save\b.+\bmonth/i.test(text) && ns.length>=2){
          const per = Math.ceil((ns[0]/ns[1])*100)/100;
          return `If your goal is ${ns[0]} over ${ns[1]} months, set aside about ${per} per month.`;
        }
        return "You said: " + text;
      }

      // --- send handler ---
      async function send(){
        const t = (input.value||'').trim();
        if(!t) return;
        const p = getProfile(); if(!p) return; // shouldn't happen

        const hist = loadHistory();
        hist.push({role:'user', text:t, ts:Date.now()}); saveHistory(hist); render(hist);
        input.value = '';

        const reply = await botReply(t);
        hist.push({role:'bot', text:reply, ts:Date.now()}); saveHistory(hist); render(hist);

        // server persist (optional)
        appendLogOnServer(p.uid, {role:'user', text:t, ts:Date.now()});
        appendLogOnServer(p.uid, {role:'bot', text:reply, ts:Date.now()});
      }

      // --- onboarding flow ---
      async function showChat(){
        pane.classList.add('hidden');
        msgEl.classList.remove('hidden');
        barEl.classList.remove('hidden');

        const p = getProfile();
        let hist = loadHistory();

        // optional: pull server history and merge if longer
        if(p){
          const srv = await loadHistoryFromServer(p.uid);
          if(srv && Array.isArray(srv.history) && srv.history.length > hist.length){
            hist = srv.history;
            saveHistory(hist);
          }
        }
        if(hist.length===0){
          const hello = greet(p?.name);
          hist.push({role:'bot', text: hello, ts: Date.now()});
          saveHistory(hist);
        }
        render(hist);
      }

      async function handleOnboard(){
        const name = (shadow.getElementById('ob-name').value||'').trim();
        const country = (shadow.getElementById('ob-country').value||'').trim();
        const email = (shadow.getElementById('ob-email').value||'').trim();

        if(!name){ alert('Please enter your name'); return; }
        if(!country){ alert('Please select your country'); return; }
        if(!validEmail(email)){ alert('Please enter a valid email'); return; }

        const existing = getProfile();
        const uid = existing?.uid || uuid();
        const profile = { uid, name, country, email };
        saveProfile(profile);

        // server register (optional)
        registerOnServer(profile);

        await showChat();
      }

      // wire UI
      toggle.addEventListener('click', ()=> {
        const min = localStorage.getItem(LS_MIN)==='1';
        setMinimized(!min);
      });
      if(sendB) sendB.addEventListener('click', send);
      if(input) input.addEventListener('keydown', e=>{ if(e.key==='Enter') send(); });
      const saveBtn = shadow.getElementById('ob-save');
      if(saveBtn) saveBtn.addEventListener('click', handleOnboard);

      // boot
      const prof = getProfile();
      if(prof){ showChat(); } else { /* stay on onboarding */ }
      const min = localStorage.getItem(LS_MIN)==='1'; setMinimized(min);
    })();
    </script>
    """

    # If you’ll run the API (below), set its base URL; else leave empty string
    api_base = ""  # e.g. "http://localhost:7861/chatapi" when API is running

    html = (
        HTML
        .replace("__TITLE__", json.dumps(title))
        .replace("__SIDE__", json.dumps(side_prop))
        .replace("__APIBASE__", json.dumps(api_base))
    )
    components.html(html, height=0, scrolling=False)
