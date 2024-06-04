import { JitsiMeeting } from '@jitsi/react-sdk';
import { useRef, useState } from 'react';

export default function Jitsi() {
    const apiRef = useRef();
    const [logItems, updateLog] = useState([]);
    const [showNew, toggleShowNew] = useState(false);
    const [knockingParticipants, updateKnockingParticipants] = useState([]);

    const generateRoomName = () => `JitsiMeetRoomNo${Math.random() * 100}-${Date.now()}`;

    const handleKnockingParticipant = payload => {
        updateLog(items => [...items, JSON.stringify(payload)]);
        updateKnockingParticipants(participants => [...participants, payload?.participant])
    };

    const handleAudioStatusChange = (payload, feature) => {
        if (payload.muted) {
            updateLog(items => [...items, `${feature} off`])
        } else {
            updateLog(items => [...items, `${feature} on`])
        }
    };

    const printEventOutput = payload => {
        updateLog(items => [...items, JSON.stringify(payload)]);
    };

    const handleChatUpdates = payload => {
        if (payload.isOpen || !payload.unreadCount) {
            return;
        }
        apiRef.current.executeCommand('toggleChat');
        updateLog(items => [...items, `you have ${payload.unreadCount} unread messages`])
    };

    const resolveKnockingParticipants = condition => {
        knockingParticipants.forEach(participant => {
            apiRef.current.executeCommand('answerKnockingParticipant', participant?.id, condition(participant));
            updateKnockingParticipants(participants => participants.filter(item => item.id === participant.id));
        });
    };

    const handleJitsiIFrameRef1 = iframeRef => {
        iframeRef.style.border = '10px solid #3d3d3d';
        iframeRef.style.background = '#3d3d3d';
        iframeRef.style.height = '400px';
        iframeRef.style.marginBottom = '20px';
    };

    const handleReadyToClose = () => {
        /* eslint-disable-next-line no-alert */
        alert('Ready to close...');
    };

    const handleApiReady = apiObj => {
        apiRef.current = apiObj;
        apiRef.current.on('knockingParticipant', handleKnockingParticipant);
        apiRef.current.on('audioMuteStatusChanged', payload => handleAudioStatusChange(payload, 'audio'));
        apiRef.current.on('videoMuteStatusChanged', payload => handleAudioStatusChange(payload, 'video'));
        apiRef.current.on('raiseHandUpdated', printEventOutput);
        apiRef.current.on('titleViewChanged', printEventOutput);
        apiRef.current.on('chatUpdated', handleChatUpdates);
        apiRef.current.on('knockingParticipant', handleKnockingParticipant);
    };

    const renderSpinner = () => (
        <div style={{
            fontFamily: 'sans-serif',
            textAlign: 'center'
        }}>
            Loading..
        </div>
    );

    // Multiple instances demo
    const renderNewInstance = () => {
        if (!showNew) {
            return null;
        }

        return (
            <JitsiMeeting
                roomName={generateRoomName()}
                getIFrameRef={handleJitsiIFrameRef2} />
        );
    };

    const handleJitsiIFrameRef2 = iframeRef => {
        iframeRef.style.marginTop = '10px';
        iframeRef.style.border = '10px dashed #df486f';
        iframeRef.style.padding = '5px';
        iframeRef.style.height = '400px';
    };

    const renderButtons = () => (
        <div style={{ margin: '15px 0' }}>
            <div style={{
                display: 'flex',
                justifyContent: 'center'
            }}>
                <button
                    type='text'
                    title='Click to execute toggle raise hand command'
                    style={{
                        border: 0,
                        borderRadius: '6px',
                        fontSize: '14px',
                        background: '#f8ae1a',
                        color: '#040404',
                        padding: '12px 46px',
                        margin: '2px 2px'
                    }}
                    onClick={() => apiRef.current.executeCommand('toggleRaiseHand')}>
                    Raise hand
                </button>
                <button
                    type='text'
                    title='Click to approve/reject knocking participant'
                    style={{
                        border: 0,
                        borderRadius: '6px',
                        fontSize: '14px',
                        background: '#0056E0',
                        color: 'white',
                        padding: '12px 46px',
                        margin: '2px 2px'
                    }}
                    onClick={() => resolveKnockingParticipants(({ name }) => !name.includes('test'))}>
                    Resolve lobby
                </button>
                <button
                    type='text'
                    title='Click to execute subject command'
                    style={{
                        border: 0,
                        borderRadius: '6px',
                        fontSize: '14px',
                        background: '#df486f',
                        color: 'white',
                        padding: '12px 46px',
                        margin: '2px 2px'
                    }}
                    onClick={() => apiRef.current.executeCommand('subject', 'New Subject')}>
                    Change subject
                </button>
                <button
                    type='text'
                    title='Click to create a new JitsiMeeting instance'
                    style={{
                        border: 0,
                        borderRadius: '6px',
                        fontSize: '14px',
                        background: '#3D3D3D',
                        color: 'white',
                        padding: '12px 46px',
                        margin: '2px 2px'
                    }}
                    onClick={() => toggleShowNew(!showNew)}>
                    Toggle new instance
                </button>
            </div>
        </div>
    );

    const renderLog = () => logItems.map(
        (item, index) => (
            <div
                style={{
                    fontFamily: 'monospace',
                    padding: '5px'
                }}
                key={index}>
                {item}
            </div>
        )
    );



    return (
        <div>
            <h1 style={{
                fontFamily: 'sans-serif',
                textAlign: 'center'
            }}>
                JitsiMeeting Demo App
            </h1>
            <JitsiMeeting
                roomName={generateRoomName()}
                spinner={renderSpinner}
                configOverwrite={{
                    subject: 'lalalala',
                    hideConferenceSubject: false
                }}
                lang='en'
                onApiReady={externalApi => handleApiReady(externalApi)}
                onReadyToClose={handleReadyToClose}
                getIFrameRef={handleJitsiIFrameRef1}
                interfaceConfigOverwrite={{
                    SHOW_JITSI_WATERMARK: false,
                    SHOW_WATERMARK_FOR_GUESTS: false,
                    DISPLAY_WELCOME_PAGE_CONTENT: false,
                    SHOW_CHROME_EXTENSION_BANNER: false,
                    SHOW_POWERED_BY: false,
                    SHOW_PROMOTIONAL_CLOSE_PAGE: true
                }}
            />
            {renderButtons()}
            {renderNewInstance()}
            {renderLog()}
        </div>
    );
}