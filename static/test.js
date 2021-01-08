const $j=jQuery.noConflict();
function getTemplateImages(game){
    return fetch('/api/?type=templates&id='+game).then((response)=>{
        if(response.status!==200){console.log('Looks like there was a problem. Status Code: '+response.status);return;
    }
    return response.json();
    }).catch((err)=>{
        console.log('Fetch Error :-S',err);
    });
}
const Tiermaker={};

Tiermaker.initList=async(code,game,editing)=>{
    const images=await getTemplateImages(game);
    code=code||JSON.parse(localStorage.getItem(`${game}-xy`))||{labels:[{text:""},{text:""},{text:""},{text:""}],images:[]};
    for(i=0;i<images.length;i++){if(i!==0){let display='inline-block';if(!editing){display='none';}

const element=`<div style='display: ${display}; 
background-image: url(/images/chart/chart/${game}/${images[i]})' 
class='draggable' id='${i}'></div>`;

$j("#inner-draggables-container").append(element);}}
if(code&&code.images){
    const images=code.images;images.forEach(element=>{
        $j('#'+element.id+'.draggable').css({top:element.y,left:element.x,position:'absolute',display:'block'});});
        $j('#top-y-input').val(code.labels[0].text);
        $j('#right-x-input').val(code.labels[1].text);
        $j('#bottom-y-input').val(code.labels[2].text);
        $j('#left-x-input').val(code.labels[3].text);}else{code={labels:["","","",""],images:[]};
    }

if(editing){
    const images=code.images;
    $j(".draggable").draggable({
        containment:"#drop",
        revert:function(dropped){},
        stop:function(){
            const $jthis=$j(this);
            const droppableId=$j(this).attr('id');
            const thisPos=$jthis.position();
            const parent=$jthis.closest('#draggable-container');
            var x=(100*parseFloat($j(this).position().left/parseFloat($j(this).parent().width())))+"%";
            var y=(parseFloat($j(this).position().top)/600)*100+"%";
            $j(this).css("left",x);
            $j(this).css("top",y);
            $j(this).css("position",'absolute');
            if(images.find((x)=>x.id===droppableId)){
                const droppableToUpdate=images.find((x)=>x.id===droppableId);
                droppableToUpdate.x=x;
                droppableToUpdate.y=y;
            }else{
                    const newDroppable={id:droppableId,x:x,y:y,};
                    images.push(newDroppable);
            }
        setCode(code);
        }});
$j("#droppable").droppable();
}




const setCode=(code)=>{
    localStorage.setItem(`${game}-xy`,JSON.stringify(code));};
    $j('#save').on("click",function(e){
        if(localStorage.getItem(`${game}-xy`)!=''&&$j("#tierTitle").val()!=''&&$j('#tierImage').val()!=''){
            $j('#tierCodeInput').val(localStorage.getItem(`${game}-xy`));$j('#tierBackground').val('#000');
            return true;
        } else if($j("#tierTitle").val()==''){alert("Please add a title to your Tier List.");
            return false;
        }else{
            alert("You must finish creating the list before saving it.");return false;}});
            $j('#close').on("click",function(e){
                $j("#overlay-logo").css('display','none');
                $j("#outer-container").css("width","100%");
                $j("#overlay").css("visibility","hidden");$j("#screenshotShow").css("display","none");});
                $j('#reset').on("click",function(e){
                    localStorage.removeItem(`${game}-xy`);location.reload();});
                    $j('.axis-text').on("input",function(e){
                        const id=$(this).attr('id');
                        const text=$(this).val();
                        if(id==='top-y-input'){code.labels[0].text=text;}
                        else if(id==='right-x-input'){code.labels[1].text=text;}
                        else if(id==='bottom-y-input'){code.labels[2].text=text;}
                        else if(id==='left-x-input'){code.labels[3].text=text;}
                        setCode(code);});
                    $j('#preview').on("click",function(e){
                        $j("#main-container").css("width","1300px");
                        $j("#screenshotShow canvas").remove();
                        $j("#screenshotShow").css("display","block");
                        $j("#overlay").css("opacity",1);
                        $j("#overlay").css("visibility","visible");
                        $j("#overlay-logo").css('display','block');
                        html2canvas($j("#draggable-container"),
                        {onrendered:function(canvas){
                            $j("#screenshotShow span").after(canvas);
                            $j("#screenshotShow").css("top","50px");
                            $j("#main-container").css("width","100%");
                            var img=canvas.toDataURL("image/png",1.0);
                            $j('#tierImage').val(img);
                            $j('#downloadLink').attr({'download':'my-image.png','href':img});
                            fetch('/includes/tracker.php?id='+game).then(()=>{console.log('updated '+game)});
                        }});
                    });
};