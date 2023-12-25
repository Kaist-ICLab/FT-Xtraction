const update_progress_interval = 500

const all_analysis_names = [overlay_names, significant_moment_names, feature_names]
const analysis_input_types = ["checkbox", "checkbox", "radio"]

//--------------------UTILS--------------------
function select_video (i) {
    if (i!=localStorage["video_index"]){
        localStorage["video_index"] = i

        var fetch_body = {
            method: "POST",
            body: JSON.stringify({"index": i}),
            headers: {"Content-type": "application/json"}
        }
        fetch("video_info/change_video", fetch_body).then(
            window.location.reload()
        )
    }
}

//--------------------PAUSE VIDEO--------------------
const pause_overlay = document.querySelector("div.pause_overlay")
var paused = true;
var video_ended = false;

pause_overlay.addEventListener("click", () => {
    paused = !paused;

    if(paused){
        pause_overlay.style["opacity"] = 1;
        clearInterval(update_progress_repeat_id)
    }

    else{
        pause_overlay.style["opacity"] = 0;
    }

    var fetch_body = {
        method: "POST",
        body: JSON.stringify({"video_paused": paused}),
        headers: {"Content-type": "application/json"}
    }
    fetch("video_info/pause_info", fetch_body).then( () =>{
        if(!paused && !video_ended){
            update_progress_repeat_id = setInterval(update_progress, update_progress_interval)
        }
    })
})

//--------------------REPLAY VIDEO--------------------
const replay_button = document.querySelector("div.replay_overlay")
replay_button.addEventListener("click", () => {
    var fetch_body = {
        method: "POST",
        body: JSON.stringify({"set_current_frame": current_frame}),
        headers: {"Content-type": "application/json"}
    }

    fetch("video_info/replay_info", fetch_body)

    paused = true
    video_ended = false

    replay_button.style["display"] = "none"
    pause_overlay.style["opacity"] = 1;
    frame_counter.innerText = 0
    timer.innerText = new Date(0 * 1000).toISOString().substring(11,19)
    progress_bar.style.setProperty("--video_progress", "0px");

    feature_chart.options.scales.x.min = 0
    feature_chart.options.scales.x.max = chart_frame_width*10
    feature_chart.update()
})

//--------------------UPDATE PROGRESS--------------------
const progress_bar = document.querySelector("div.video_progress_bar")
const timer = document.querySelector("div.timer")
const frame_counter = document.querySelector("div.frame_counter")

const progress_bar_left = progress_bar.getBoundingClientRect().left
const progress_bar_width = progress_bar.clientWidth

var mouse_diff = 0
var progress_percent = 0
var current_frame = 0
var seconds = 0
var current_time = new Date()

progress_bar.addEventListener("click", (event) => {
    mouse_diff = event.clientX - progress_bar_left
    progress_bar.style.setProperty("--video_progress", `${mouse_diff}px`);
    progress_percent = mouse_diff/progress_bar_width
    current_frame = Math.floor(progress_percent*total_frame_count)
    seconds = current_frame/fps

    frame_counter.innerText = current_frame
    timer.innerText = new Date(seconds * 1000).toISOString().substring(11,19)

    feature_chart.options.scales.x.min = current_frame<total_frame_count-chart_frame_width*10 ? current_frame : total_frame_count-chart_frame_width*10
    feature_chart.options.scales.x.max = current_frame<total_frame_count-chart_frame_width*10 ? current_frame+chart_frame_width*10 : total_frame_count
    feature_chart.update()

    var fetch_body = {
        method: "POST",
        body: JSON.stringify({"set_current_frame": current_frame}),
        headers: {"Content-type": "application/json"}
    }
    clearInterval(update_progress_repeat_id)
    fetch("video_info/frame_info", fetch_body).then( () => {
        console.log("SET AT SKIP")
        update_progress_repeat_id = setInterval(update_progress, update_progress_interval)
    })
})

function get_current_frame(){
    var fetch_body = {
        method: "POST",
        body: JSON.stringify({message:"message"}),
        headers: {"Content-type": "application/json"}
    }

    fetch("video_info/frame_info", fetch_body).then(
        function(response) {return response.json();}
    ).then(
        function(data) {
            current_frame = data.current_frame;
            if(data.video_ended){
                video_ended = true;
                console.log("ENDED")
                replay_button.style["display"] = "flex"
                clearInterval(update_progress_repeat_id)
            }
        }
    )
}

function update_progress(){
    if (!paused && !video_ended){
        get_current_frame()
        var seconds = current_frame/fps
        var moving_progress_percent = current_frame/total_frame_count

        progress_bar.style.setProperty("--video_progress", `${progress_bar.clientWidth*moving_progress_percent}px`);

        frame_counter.innerText = current_frame
        timer.innerText = new Date(seconds * 1000).toISOString().substring(11,19)

        feature_chart.options.scales.x.min = current_frame<total_frame_count-chart_frame_width*10 ? current_frame : total_frame_count-chart_frame_width*10
        feature_chart.options.scales.x.max = current_frame<total_frame_count-chart_frame_width*10 ? current_frame+chart_frame_width*10 : total_frame_count
        feature_chart.update()
    }
}

var update_interval_id = setInterval(update_progress, update_progress_interval)

//--------------------SIGNIFICANT MOMENTS--------------------
function link_significant_moments(sig_moment_ind, input_j){
    const sig_moment_div_i = document.createElement("div")
    sig_moment_div_i.className = "significant_moment_container"

     for(let j=0; j<significant_moment_data[sig_moment_ind].length; j++){
         let sig_moment_j = document.createElement("div")
         sig_moment_j.className = "significant_moment"
         sig_moment_j.style["left"] = `${significant_moment_data[sig_moment_ind][j]/total_frame_count*100}%`
         sig_moment_j.style["background-color"] = significant_moment_colors[sig_moment_ind]
         console.log(significant_moment_colors)
         sig_moment_div_i.appendChild(sig_moment_j)
     }
     console.log(total_frame_count)
     progress_bar.appendChild(sig_moment_div_i)

     input_j.addEventListener("click", () => {
         if(input_j.checked){
             sig_moment_div_i.style.display = "flex"
         }
         else{
             sig_moment_div_i.style.display = "none"
         }
     })
}

//--------------------VIDEO SELECTION--------------------
const video_selection_form = document.querySelector("form.video_selection_form")
for(let i=0; i<video_names.length; i++){
    const input_container_i = document.createElement("div")
    input_container_i.className = "video_selection_input_container"

    const input_i = document.createElement("input")
    input_i.type = "radio"
    input_i.className = "video_selection_input"
    input_i.id = `video_selection_input_${i}`
    input_i.name = "video_selection_input"

    const label_i = document.createElement("label")
    label_i.className = "video_selection_label"
    label_i.htmlFor = `video_selection_input_${i}`
    label_i.innerText = video_names[i]

    input_container_i.appendChild(input_i)
    input_container_i.appendChild(label_i)
    video_selection_form.appendChild(input_container_i)

    input_i.addEventListener("click", () => {
        select_video(i)
    })
}

document.querySelectorAll("input.video_selection_input")[current_video_ind].checked = true

//--------------------VIDEO OVERLAY SELECTION--------------------
function link_video_overlays(video_overlay_ind, input_j){
    input_j.addEventListener("click", () => {
        overlay_flags[video_overlay_ind] = input_j.checked
        var fetch_body = {
            method: "POST",
            body: JSON.stringify({"overlay_flags": overlay_flags}),
            headers: {"Content-type": "application/json"}
        }
        fetch("video_info/overlay_info", fetch_body)
    })
}

//--------------------ANALYSIS TYPE SELECTION--------------------
const analysis_type_selection_radios = document.querySelectorAll("input.analysis_type_selection_radio")
for(let i=0; i<analysis_type_selection_radios.length; i++){
    analysis_type_selection_radios[i].addEventListener("click", () => {
        for(let j=0; j<analysis_forms.length; j++){
            if(i==j){
                analysis_forms[j].style["display"] = "block"
            }
            else{
                analysis_forms[j].style["display"] = "none"
            }
        }
    })
}

//--------------------ANALYSIS SELECTION--------------------
const analysis_forms = document.querySelectorAll("form.analysis_selection_form")

const input_linking_handlers = [link_video_overlays,link_significant_moments,link_chart_features]

for(let i=0; i<analysis_forms.length; i++){
    let form_i = analysis_forms[i]
    for(let j=0; j<all_analysis_names[i].length; j++){
        const input_container_j = document.createElement("div")
        input_container_j.className = "analysis_selection_input_container"

        const input_j = document.createElement("input")
        input_j.type = analysis_input_types[i]
        input_j.id = `analysis_selection_input_${i}_${j}`
        input_j.className = "analysis_selection_input"
        if(analysis_input_types[i] == "radio"){
            input_j.name = "analysis_selection_radio"
        }
        if((i==2) && (j==0)){
            input_j.checked = true;
        }

        const label_j = document.createElement("label")
        label_j.className = "analysis_selection_label"
        label_j.innerText = all_analysis_names[i][j]
        label_j.htmlFor = `analysis_selection_input_${i}_${j}`

        input_container_j.appendChild(input_j)
        input_container_j.appendChild(label_j)
        form_i.appendChild(input_container_j)

        input_linking_handlers[i](j, input_j)
    }
}

// //--------------------FEATURE CHART--------------------
const dataset = []

for(let i=0; i<feature_names.length; i++){
    for(let j=0; j<sub_feature_names[i].length; j++){
        let color_array_j = graph_colors[i][j]
        
        let dataset_j = {
            label: feature_names[i],
            data: Object.fromEntries(feature_data[i][j].map((x,k) => [frames[k], feature_data[i][j][k]])),
            backgroundColor: [`rgba(${color_array_j[0]}, ${color_array_j[1]}, ${color_array_j[2]}, 0.5)`],
            borderColor: [`rgba(${color_array_j[0]}, ${color_array_j[1]}, ${color_array_j[2]}, 1)`],
            borderWidth: 1,
            hidden: true
        }

        dataset.push(dataset_j);
    }
}

const data = {datasets: dataset}

const config = {
    type: 'line',
    data,
    options: {
        spanGaps: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            x: {
                type: "linear",
                min: 0,
                max: 100,
                ticks: {
                    stepSize:10,
                    color: "rgba(0, 117, 74,1)"
                },
                grid: {
                    color: "rgba(0, 117, 74,0.5)"
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: "rgba(0, 117, 74,0.5)"
                },
                ticks:{
                    color: "rgba(0, 117, 74,1)"
                }
            }
        }
    }
};

const feature_chart = new Chart(
    document.querySelector("canvas.feature_chart"),
    config
);

// //-----SUB FEATURE SELECTION-----
const feature_chart_legend = document.querySelector("div.feature_chart_legend_container")
const feature_analysis_selectors = document.querySelectorAll("input[type='radio'].analysis_selection_input")
let feature_chart_legend_forms = []
const feature_legend_elements = []

for(let i=0; i<feature_names.length; i++){
    const feature_legend_elements_i = []
    let form_i = document.createElement("form")
    form_i.style["display"] = "none"
    form_i.className = "feature_chart_legend_form"
    
    for(let j=0; j<sub_feature_names[i].length; j++){
        const input_container_j = document.createElement("div")
        input_container_j.className = "feature_chart_legend_input_container"

        const input_j = document.createElement("input")
        input_j.type = "checkbox"
        input_j.id = `feature_chart_legend_input_${i}_${j}`
        input_j.className = "feature_chart_legend_input"
        input_j.checked = true

        const label_j = document.createElement("label")
        label_j.className = "feature_chart_legend_label"
        label_j.innerText = sub_feature_names[i][j]
        label_j.htmlFor = `feature_chart_legend_input_${i}_${j}`

        input_container_j.appendChild(input_j)
        input_container_j.appendChild(label_j)
        
        let color_array_j = graph_colors[i][j]
        input_container_j.style.setProperty("--checkbox_color", `rgb(${color_array_j[0]}, ${color_array_j[1]}, ${color_array_j[2]})`)
        input_container_j.style.setProperty("--checkbox_border_color", `rgb(${color_array_j[0]}, ${color_array_j[1]}, ${color_array_j[2]})`)
        input_container_j.style["background-color"] = `rgba(${color_array_j[0]}, ${color_array_j[1]}, ${color_array_j[2]}, 0.3)`
        
        form_i.appendChild(input_container_j)
        feature_chart_legend.appendChild(form_i)
        feature_legend_elements_i.push(input_container_j)

        input_j.addEventListener("click", () => {
            if(input_j.checked){
                feature_chart.setDatasetVisibility(feature_offsets[i]+j, true)
                feature_legend_elements[i][j].classList.remove("fade")
            }
            else{
                feature_chart.setDatasetVisibility(feature_offsets[i]+j, false)
                feature_legend_elements[i][j].classList.add("fade")
            }
            feature_chart.update()
        })
    }

    feature_legend_elements.push(feature_legend_elements_i)
    feature_chart_legend_forms.push(form_i)
}

function link_chart_features(chart_feature_ind, input_k){
    input_k.addEventListener("click", () => {
        for(let i=0; i<feature_names.length; i++){
            let form_i = feature_chart_legend_forms[i]
            let form_i_children = form_i.children
            if(i==chart_feature_ind){
                form_i.style["display"] = "block"

                for(let j=0; j<form_i_children.length; j++){
                    var is_hidden = feature_legend_elements[i][j].classList.contains("fade")
                    feature_chart.setDatasetVisibility(feature_offsets[i]+j, !is_hidden);
                }
                
            }
            else{
                form_i.style["display"] = "none"

                for(let j=0; j<form_i_children.length; j++){
                    feature_chart.setDatasetVisibility(feature_offsets[i]+j, false);
                }
            }
        }
        feature_chart.update()
    }) 
}

//--------------------MISC.--------------------
//-----INITLIAZING INPUT BOXES-----
analysis_forms[0].style["display"] = "block"
feature_chart_legend_forms[0].style["display"] = "block"

for(let i=0; i<sub_feature_names[0].length; i++){
    dataset[i]["hidden"]=false;
}

feature_chart.update()