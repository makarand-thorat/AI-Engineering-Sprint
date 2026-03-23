import streamlit as st
import requests
import json

st.set_page_config(page_title="Corporate Scout v2", page_icon="🕵️‍♂️")

st.title("🕵️‍♂️ Corporate Scout & Drafter")
st.markdown("### Day 29: Production Grade UI & Guardrails")

# Input Fields
company = st.text_input("Target Company:", placeholder="e.g. NVIDIA")
objective = st.text_input("Partnership Goal:", placeholder="e.g. GPU optimization for our LLM stack")

if st.button("Generate Research & Email"):
    if not company or not objective:
        st.error("Please provide both a company name and an objective.")
    else:
        with st.chat_message("assistant"):
            
            placeholder = st.empty()
            full_content = ""
            
            
            url = "http://localhost:8000/chat"
            payload = {"message": f"Research {company} for the following goal: {objective}"}
            
            try:
                
                with requests.post(url, json=payload, stream=True) as response:
                    for line in response.iter_lines():
                        if line:
                            
                            decoded_line = line.decode('utf-8').replace('data: ', '')
                            try:
                                data = json.loads(decoded_line)
                                chunk = data.get("text", "")
                                
                                
                                full_content += chunk
                                placeholder.markdown(full_content + "▌")
                            except json.JSONDecodeError:
                                continue
                                
                
                placeholder.markdown(full_content)
                print(f"this is {full_content}")

                if not full_content:
                    st.warning("⚠️ Policy Violation: Request Blocked by Guardrails.")
                else:
                    st.success("✅ Research & Drafting Complete!")

                if full_content:

                    st.divider()
                    with st.spinner("📊 Running AI Quality Audit..."):

                        try:

                            # 2. Send the final email to the evaluation endpoint
                            eval_response = requests.post(
                                "http://localhost:8000/evaluate", 
                                json={"content": full_content}
                            )
                            eval_data = eval_response.json()

                            # 3. Display results in the Sidebar
                            with st.sidebar:
                                st.header("📈 Agent Report Card")
                                st.metric(label="Quality Score", value=f"{eval_data['score']}/10")
                                
                                st.subheader("Auditor Notes")
                                st.write(eval_data['reasoning'])
                                
                                if eval_data['score'] >= 8:
                                    st.success("✅ High Quality - Ready to Send")
                                else:
                                    st.warning("⚠️ Review Required - Fact Density Low")
                        except Exception as e:
                            st.error(f"Evaluation failed: {e}")

                
            except Exception as e:
                st.error(f"Connection Error: {e}")
