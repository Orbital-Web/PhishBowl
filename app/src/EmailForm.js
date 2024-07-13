import React from 'react';

function EmailForm() {
    return (
        <div className="form">
            <h2>Email Form</h2>
            <form>
                <div>
                    <label>Subject:</label>
                    <input type="text" name="subject" />
                </div>
                <div>
                    <label>Sender:</label>
                    <input type="text" name="sender" />
                </div>
                <div>
                    <label>Body:</label>
                    <textarea name="body" />
                </div>
            </form>
        </div>
    );
}

export default EmailForm;
