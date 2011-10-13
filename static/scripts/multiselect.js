/*******************************************************************************

jQuery MultiSelect v1.1
(c) Arc90, Inc.

Based off of MultiSelect v1.0 by Joel Nagy,
based off the jQueryMultiSelect by Chris Dary.

http://www.arc90.com
http://lab.arc90.com

Licensed under :
    Creative Commons Attribution 3.0 http://creativecommons.org/licenses/by/3.0/

When:       Who:    What:
-----       ----    -----
20-Nov-07   Ben S   Continued port.
21-Nov-07   Ben S   Additional fixes, formatting issues, bug fixes.
26-Nov-07   Ben S   Added 'hand' cursor, added <li> and <label> select.
27-Nov-07   Ben S   Bug fix, lab display page. Removed timeout configuration.
                    multiSelect now stays open until the user clicks outside
                    its bounds or clicks the title. Added width support.
19-Mar-08   Ben S   Fixed BUG:015.

USAGE:
------

$('#identifier').multiSelect();
$('#identifier').multiSelect({option: optionValue});
  
Example:
$('#lang').multiSelect({
                        select_all_min: 3,
                        no_selection: "Nothing selected",
                        selected_text: " selected",
                       });

OPTIONS:
--------

no_selection    = 'No selection';
selected        = 'Options selected';
selectAllMin    = 6;

Not implemented:
msSeparator     = '|';
a$.msBodyTimer  = null;

Removed:
timeout         = 1500

BUGS:
-----

BUG:001:    When the drop down has been collasped and closed, a mouse movement
            over the title causes the timeout to be set to null and immediatly
            after causes the dropdown to collaspe. This is caused when the
            timeout reset code calls clickTitle( ).
FIX:001:    Added select_state, which allows us to know the current state
            of the dropdown, collapsed or closed.


BUG:002:    SelectAllMin is not being set.
FIX:002:    SelectAllMine optional argument changed to match existing code,
            select_all_min.


BUG:004:    Default selected items are not bold.
FIX:004:    Default items selected are now bold. Thanks Chris D.


BUG:005:    Selectbox title does not reflected default selected items.
FIX:005:    Selectbox title now reflects default items.


BUG:006:    Optional 'selected' arguments does not work.
FIX:006:    Changed 'selected' to 'selected_text'.


BUG:007:    List items are not visible
FIX:007:    Added the checkBoxID label.


BUG:008:    Selected items are not being sent via GET. It appears the checkboxes
            are being selected, but the selectList item is not. Same for unchecked
            items, those are still being propogated via GET.
FIX:008:    After we attach the new multiSelect to the DOM, we remove the original
            select box. This causes the multiSelect items to be sent via GET.
            Thanks again Chris D!


BUG:009:    The select-all checkbox id is set statically, causing multiple
            multiSelects on the same page to error.
FIX:009:    Checkbox id's and name's are created unique.
        

BUG:010:    Checkboxes do not get 'checked' when a user chooses to 'Select All'
            on XP/SP2 IE 5.55.


BUG:011:    Selectboxes below the multiSelect 'bleed through' on XP/SP2 IE 6.0
            and below.


BUG:012:    Mouseover graphic does not load (IE Only 5.55, 6 & 7)
            FIX On IE 7.


BUG:013:    Default select title sizes are too small (width & height).
FIX:013:    Conditional CSS added to *attempt* to fix this on IE 6 & 5.55.

BUG:014:    A multiSelect with no arguments failed to build.
FIX:014:    Moved the 'select all' code into the the 'select all' conditional.

BUG:015:    Submitted by anthony ryan delorie - "Also the Select All shows the number 
	    of actual selections plus one (counting the select all selected) unlike 
            Joel Nagy's code where it correctly shows the number."
FIX:015:    Fixed provided by Jose.

Tested on the following browsers/platforms:
-------------------------------------------
XP/SP2:
    IE 7.0      - No Bugs
    IE 6.0      - Bug 011, 012
    FF 2.0      - No bugs
    Safari 3.0  - No bugs
    Opera 9.2   - No bugs
    IE 5.55     - Bug 010, 011, 012

*******************************************************************************/


/* Global variables. */
var multiSelect_timer = null;  /* handle mouseouts. */
var select_state      = false; /* false = closed, true = open */
var is_clicked        = false; /* false = checkbox has not been clicked
                                  true  = checkbox has been clicked
                               */


/*@function multiSelect
  @description Creates a multiselect box w/checkboxes allowing a
                       user to select multiple items. We also provide a
                       dynamically updating title field, that displays the
                       current total of selected items (or none).
  @param options An array of possible configuration values.
*/
jQuery.fn.multiSelect = function(options)
{
    /* Sets the default options, if non are provided.  */
    if(!options) options = {};
    
    /* Title text displayed when no items are selected. */
    var no_selection   = options.no_selection  || "No selection";
    
    /* Title text displayed when one or more items are selected. */
    var selected_text  = options.selected_text || " Options selected";
    
        /* Minimun number of items a selectbox must have in order to display
       the 'select all' option.
    */
    var select_all_min = typeof(options.select_all_min) != 'undefined'
                       ? options.select_all_min : 6;    
    
    return this.each(function()
    {
        /* Timeout passed to setTimeout( ). */
        var timeout = 0;
    
        /*@function multiSelect_closeWindow
          @description Closes the multiSelect by clicking the title
          and unbinding the click( ) to the body.
        */
        function multiSelect_closeWindow( )
        {
            selectTitle.click( );
            $('body').unbind("click", multiSelect_closeWindow);
        }
                        
        /* Workflow:
            1. Set up the HTML elements that will display the multiSelect.
            2. Bind the events that will display the HTML elements.
            3. Hide the original select box.
        */
        var hiddenSet = new Array( );

        var id    = $(this).attr('id');
        var title = $(this).attr('title');
        var name  = $(this).attr('name');

        /* Code taken from the original multiSelect. */
        var fieldWidth = this.className.toLowerCase().indexOf('fieldwidth-');
        var valueWidth = this.className.toLowerCase().indexOf('valuewidth-');
        
        if (fieldWidth >= 0)
        {
            var q = this.className.slice(fieldWidth);
            fieldWidth = (q.slice(0, q.indexOf(' ') < 0? q.length: q.indexOf(' '))).slice('fieldwidth-'.length);
            fieldWidth = parseFloat(fieldWidth) == fieldWidth? fieldWidth+'px': fieldWidth;
        }
        else fieldWidth = '';
        
        if (valueWidth >= 0)
        {
            var q = this.className.slice(valueWidth);
            valueWidth = (q.slice(0, q.indexOf(' ') < 0? q.length: q.indexOf(' '))).slice('valuewidth-'.length);
            valueWidth = parseFloat(valueWidth) == valueWidth? valueWidth+'px': valueWidth;
        }
        else valueWidth = '';        

        /*** STEP 1: Set up the HTML elements that will display the multiSelect */

        /* Create our container elements */
        var selectDiv   = $('<div id="multiSelect-' + id + '" class="multiSelect">');
        var selectTitle = $('<div id="multiSelect-' + id
                        + '-title" class="title" title="' + title
                        + '">').text(no_selection);
        
        selectTitle.css('width', fieldWidth);
        selectDiv.css('width', valueWidth);
        
        var selectContent = $('<div id="multiSelect-' + id
                          + '-content" class="multiSelectContent collapsed">');
        var selectList    = $('<ul>');

        /* Set up their heirarchy (selectDiv contains selectTitle, selectContent contains selectList) */
        selectDiv.append(selectTitle);
        selectContent.append(selectList);
        
        /* When the user clicks the select box title, display the contents. */
        selectTitle.click(function()
        {
            select_state = ( select_state )? false : true;
            selectContent.toggleClass('collapsed');
        });
        
        /* if selectContent is moused out, only close the list if
           the user clicks the body.
        */
        jQuery([selectDiv.get(0), selectContent.get(0), selectList.get(0)]).mouseout(function()
        {
            multiSelect_timer = setTimeout(function()
            {
                if(multiSelect_timer != null)
                {
                    clearTimeout(multiSelect_timer);
                    multiSelect_timer = null;
                    if ( select_state == true )
                    {
                        $('body').bind("click", multiSelect_closeWindow);
                    }
                }
            }, timeout); 
        });


        /* Clear the timeout if selectContent is moused over. This removes the
           bind on the body click, allowing the user to click on the list
           without it closing.
        */
        jQuery([selectDiv.get(0), selectContent.get(0), selectList.get(0)]).mouseover(function()
        {
            $('body').unbind("click", multiSelect_closeWindow);
            if ( multiSelect_timer == null ) return;
            clearTimeout(multiSelect_timer);
            multiSelect_timer = null;
        });

        /* If the select all option is configured, display it. */
        if(jQuery('option',this).length >= select_all_min)
        {
            var li = jQuery('<li class="a9selectall">').appendTo(selectList);
            var checkbox = jQuery('<input type="checkbox" id="multiSelect-options-selectAll-' +id+ '" name="multiSelect-options-selectAll-' +id+'" value="1" title="Select All" />').appendTo(li);
            var label = jQuery('<label for="multiSelect-options-selectAll">Select All</label>').appendTo(li);
            
            /* Set the cursor. */
            setHandCursor(checkbox, label);
            
            /* Called when a user clicks on the 'Select All' checkbox. */       
            checkbox.click(function()
            {
                toggleAllLabelsAndCheckboxes(this.checked, selectList, true);
                updateSelectTitle(selectList, selectTitle);
                is_clicked = true; /* Don't run the <li> code. */
            });
            
            /* Called when a user clicks on the 'Select All' <label>. */
            label.click(function( )
            {
                toggleAllLabelsAndCheckboxes(Boolean($('input', $(this).parent()).attr('checked')),
                                       selectList, false);
                updateSelectTitle(selectList, selectTitle);            
                is_clicked = true; /* Don't run the <li> code. */
            });
            
            /* Called when a user clicks the 'Select All' <li>. */
            li.click(function()
            {
                if ( is_clicked == false )
                {
                    toggleAllLabelsAndCheckboxes(Boolean($(':checkbox', $(this)).attr('checked')),
                                                   selectList, false);
                    updateSelectTitle(selectList, selectTitle);
                }
                is_clicked = true;
            });
        }

            
        /* Constructs the selectboxes. Happens everytime. */
        jQuery('option',this).each(function(i)
        {
            // Helper variables
            var value      = jQuery(this).attr('value');
            var text       = jQuery(this).text();
            var isSelected = $(this).attr('selected') == true? 'checked="yes"' : '';
            
            var fontWeight = ( isSelected != '' )? 'bold' : 'normal';
            var checkBoxID = 'multiSelect-options-' + id + '-' + i;

            var li = jQuery('<li>').appendTo(selectList);
                
            /* Construct the checkbox. */
            var checkbox = jQuery('<input type="checkbox" id="' + checkBoxID
                         + '" name="multiSelect-options-' + id + '[]" value="' + value
                         + '" title="' + text + '"' + isSelected + '/>').appendTo(li);
            
            var label = jQuery('<label for="' + checkBoxID
                      + '">' + checkBoxID + '</label>').text(text).css('font-weight', fontWeight).appendTo(li);           
            
            /* Set the cursor. */
            setHandCursor(checkbox, label);
            
            /* Update the title. */ 
            updateSelectTitle(selectList, selectTitle);
                    
            /* The user has selected a checkbox:
               1. Bold the selected element
               2. Update the title
            */
            checkbox.click(function()
            {
                /* Bold if checked, unbold if unchecked. */
                fontWeight = ( this.checked == 1 )? 'bold' : 'normal';
                $('label', $(this).parent( )).css('font-weight', fontWeight);
                
                /* Update the title. */
                updateSelectTitle(selectList, selectTitle);
                
                /* We do not want the <li> or <label> code to run. */
                is_clicked = true;
            });
        });
        
        /* The user selected the <label>. Record this because
           we only want the list events to happen once.
        */
        $('label', selectList).click(function( )
        {
            is_clicked = true;
        });

        /* When a user selects any portion of the <li>
           element toggle the checkbox and label.
        */
        $('li', selectList).click(function()
        {
            if ( is_clicked == false )
            {
                var fontWeight = 'normal'; /* Default state. */
                var isChecked  = '';       /* Default state. */
                
                if( $(':checkbox', $(this)).attr('checked') != true )
                {
                    isChecked  = 'checked';
                    fontWeight = 'bold';
                }

                $('label', $(this)).css('font-weight', fontWeight);
                $(':checkbox', $(this)).attr('checked', isChecked);

                /* Update the title. */
                updateSelectTitle(selectList, selectTitle);
            }
            is_clicked = false;
        });

        /* Attach the multiSelect to the DOM */
        jQuery(this).before(selectDiv);
        jQuery(this).before(selectContent);

        /* Remove the selectbox, identified by 'id' because we only want
           to show the div checkboxes.
        */
        $(this).remove('#' + id);
    });


    /*@function     toggleAllLabelsAndCheckboxes
      @description  Toggles the state of all the checkboxes within the
                    multiSelect, plus applies bold or normal weight to the
                    <label>s.
      @param        checked     Is the selected checkbox checked or not.
      @param        selectList  The list elements.
      @param        condition   A boolean value used for comparision.
    */
    function toggleAllLabelsAndCheckboxes(checked, selectList, condition)
    {
        var fontWeight = 'normal'; /* Default state. */
        var isChecked  = '';       /* Default state. */

        /* If 'select all' is checked we set font-weight to 'bold',
           otherwise set it to 'normal'.
        */
        if ( checked == condition )
        {
            isChecked  = 'checked';
            fontWeight = 'bold';
        }

        $('label',selectList).css({'font-weight':  fontWeight});
        $(':checkbox', selectList).attr('checked', isChecked);        
    }
    
    
    /*@function     setHandCursor
      @description  Changes the cursor from a pointer to a hand.
     
      @param        checkbox
      @param        label
    */
    function setHandCursor(checkbox, label)
    {
        checkbox.css('cursor', 'pointer');
        checkbox.css('cursor', 'hand');
        label.css('cursor',    'pointer');
        label.css('cursor',    'hand'); 
    }
    
    
    /*@function    updateSelectTitle
      @description Calculates the number of currently checked items
                               and updates the select box title to reflect that.
      @param       selectList
      @param       selectTitle
    */
    function updateSelectTitle(selectList, selectTitle)
    {
        /* Calculate the total checked items. */
	var selectCount = $('li:not(.selectall) :checkbox:checked', selectList).length+1 - (this.checked ? 1 : 1);
        
        /* Update the title: 'n selected' || 'No selection'. */
        selectTitle.text(selectCount > 0 ? (selectCount + selected_text) : no_selection);
    }
}