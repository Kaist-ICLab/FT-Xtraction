//--------------------DATA--------------------
let video_checkboxes = []
let update_progress_interval = 100

//--------------------VIDEO-CSV TABLE--------------------
const table_body = document.querySelector("table.video_csv_list>tbody")
let video_csv_csv_founds = []
let video_csv_num_features = []
for(let i=0; i<video_names.length; i++){
    let tr_i = document.createElement("tr")
    let td_i0 = document.createElement("td")
    let td_i1 = document.createElement("td")
    let td_i2 = document.createElement("td")
    let td_i3 = document.createElement("td")
    let input_i = document.createElement("input")
    input_i.type = "checkbox"

    td_i1.innerText = video_names[i]
    td_i2.innerText = csv_found[i]
    td_i3.innerText = num_features[i]

    td_i0.appendChild(input_i)
    tr_i.appendChild(td_i0)
    tr_i.appendChild(td_i1)
    tr_i.appendChild(td_i2)
    tr_i.appendChild(td_i3)

    table_body.appendChild(tr_i)
    video_csv_csv_founds.push(td_i2)
    video_csv_num_features.push(td_i3)

    tr_i.addEventListener("click", () => {
        input_i.checked = !input_i.checked
        selected_videos[i] = input_i.checked
    })
    input_i.addEventListener("click", () => {
        input_i.checked = !input_i.checked
        selected_videos[i] = input_i.checked
    })

    video_checkboxes.push(input_i)
}

//--------------------SELECT ALL--------------------

const select_all = document.querySelector("div.select_all")

select_all.addEventListener("click", () => {
    for(let i=0; i<video_checkboxes.length; i++){
        video_checkboxes[i].checked=true;
        selected_videos[i] = video_checkboxes[i].checked
    }
})

//--------------------FEATURE LIST--------------------
const feature_list_form = document.querySelector("form.feature_list_form")
for(let i=0; i<features.length; i++){
    
    const input_container_i = document.createElement("div")
    input_container_i.className = "input_feature_list_container"

    const input_i = document.createElement("input")
    input_i.type = "checkbox"
    input_i.className = "feature_list_input"
    input_i.id = `feature_${i}`


    const label_i = document.createElement("label")
    label_i.className = "feature_list_label"
    label_i.htmlFor = `feature_${i}`
    label_i.innerText = features[i]

    input_container_i.appendChild(input_i)
    input_container_i.appendChild(label_i)
    feature_list_form.appendChild(input_container_i)

    input_i.addEventListener("click", () => {
        selected_features[i] = !selected_features[i]
    })
}

//--------------------SIGNFICANT MOMENTS LIST--------------------

const significant_moments_list_form = document.querySelector("form.significant_moments_list_form")
for(let i=0; i<signficant_moments.length; i++){
    
    const input_container_i = document.createElement("div")
    input_container_i.className = "input_significant_moment_list_container"

    const input_i = document.createElement("input")
    input_i.type = "checkbox"
    input_i.className = "significant_moment_list_input"
    input_i.id = `significant_moment_${i}`


    const label_i = document.createElement("label")
    label_i.className = "significant_moment_list_label"
    label_i.htmlFor = `significant_moment_${i}`
    label_i.innerText = signficant_moments[i]

    input_container_i.appendChild(input_i)
    input_container_i.appendChild(label_i)
    significant_moments_list_form.appendChild(input_container_i)

    input_i.addEventListener("click", () => {
        selected_significant_moments[i] = !selected_significant_moments[i]
    })
}

//--------------------CREATE CSV--------------------
const create_csv_overlay = document.querySelector("div.csv_progress_overlay")
const create_csvs = document.querySelector("div.create_csvs")
const progress_table_body = document.querySelector("table.csv_progress_table>tbody")
const finished_processing_message = document.querySelector("div.finished_processing_message")
const close_progress_overlay_button = document.querySelector("div.close_progress_overlay")
const stop_processing_button = document.querySelector("div.stop_processing")
let processing_vid_times = []
let processing_vid_percents = []
let hold_selected_vids = []
let previous_ind = 0
var vid_ind = 0
var update_progress_id=0


create_csvs.addEventListener("click", () => {
    create_csv_overlay.style["display"]="flex"
    finished_processing_message.style["display"]="none"

    close_progress_overlay_button.style["opacity"]=0.5
    close_progress_overlay_button.style["cursor"]="default"
    close_progress_overlay_button.removeEventListener("click", close_progress_overlay)

    stop_processing_button.style["opacity"]=1
    stop_processing_button.style["cursor"]="pointer"
    stop_processing_button.addEventListener("click", stop_processing)

    for(let i=0; i<selected_videos.length; i++){
        if(selected_videos[i]){
            hold_selected_vids.push(i)

            let tr_i = document.createElement("tr")
            let td_i0 = document.createElement("td")
            let td_i1 = document.createElement("td")
            let td_i2 = document.createElement("td")
            td_i2.style["width"]="15%"
            // let progress_container_i = document.createElement("div")
            // progress_container_i.className = "csv_progress_bar"


            td_i0.innerText = video_names[i]
            td_i1.innerText = "WAITING"
            td_i2.innerText = "0%"

            tr_i.appendChild(td_i0)
            tr_i.appendChild(td_i1)
            tr_i.appendChild(td_i2)
            progress_table_body.appendChild(tr_i)
            processing_vid_times.push(td_i1)
            processing_vid_percents.push(td_i2)
        }
        else{
            processing_vid_times.push(null)
            processing_vid_percents.push(null)
        }
    }

    previous_ind = hold_selected_vids[0]

    var fetch_body = {
        method: "POST",
        body: JSON.stringify({"video_indices": selected_videos, "selected_features": selected_features, "selected_significant_moments": selected_significant_moments}),
        headers: {"Content-type": "application/json"}
    }

    update_progress_id = setInterval(update_progress, update_progress_interval)

    fetch("extraction_info", fetch_body).then(function(response) {return response.json();}).then(function(data) {clearInterval(update_progress_id); handle_end_of_processing()})

})

function update_progress(){

    var fetch_body = {
        method: "POST",
        body: JSON.stringify({message:"message"}),
        headers: {"Content-type": "application/json"}
    }

    fetch("extraction_progress", fetch_body).then(
        function(response) {return response.json();}
    ).then(
        function(data) {
            vid_ind = data["current_video"]
            processing_vid_percents[vid_ind].innerText = data["processing_progress"]
            processing_vid_times[vid_ind].innerText = data["est_time"]
            if(vid_ind!=previous_ind){
                processing_vid_percents[previous_ind].innerText = "FINISHED"
                processing_vid_times[previous_ind].innerText = "FINISHED"
                previous_ind=vid_ind
            }
        }
    )
}


function handle_end_of_processing(){
    var fetch_body = {
        method: "POST",
        body: JSON.stringify({}),
        headers: {"Content-type": "application/json"}
    }

    fetch("update_lists", fetch_body).then(
        function(response) {
            return response.json();
        }
    ).then(
        function(data) {
            csv_found = data["csv_exists_list"]
            num_features = data["number_features"]
            
            for(let i=0; i<csv_found.length; i++){
                video_csv_csv_founds[i].innerText = csv_found[i]
                video_csv_num_features[i].innerText = num_features[i]
            }
            while (progress_table_body.firstChild) {
                progress_table_body.removeChild(progress_table_body.lastChild);
            }

            finished_processing_message.style["display"]="flex";

            close_progress_overlay_button.style["opacity"]=1
            close_progress_overlay_button.style["cursor"]="pointer"
            close_progress_overlay_button.addEventListener("click", close_progress_overlay)

            stop_processing_button.style["opacity"]=0.5
            stop_processing_button.style["cursor"]="default"
            stop_processing_button.removeEventListener("click", stop_processing)

            processing_vid_times = []
            processing_vid_percents = []
            hold_selected_vids = []
            previous_ind = 0
            vid_ind = 0
            update_progress_id=0
    }) 
}

function close_progress_overlay(){
    create_csv_overlay.style["display"]="none";
}


function stop_processing(){
    var fetch_body = {
        method: "POST",
        body: JSON.stringify({}),
        headers: {"Content-type": "application/json"}
    }
    fetch("stop_processing", fetch_body).then(() => {
        close_progress_overlay()
    })
}



