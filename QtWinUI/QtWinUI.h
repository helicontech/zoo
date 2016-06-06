#pragma once

#include <QtWidgets/QApplication>
#include <QtWidgets/QMainWindow>
#include <QtCore/QProcess>
#include <QtWebKitWidgets/QWebView>

#include "resource.h"

namespace boottraper {
    typedef int         Milliseconds;

    ///CustomWebView is needed to create new separate WebView window by request from JS
    struct CustomWebView : public QWebView {
        explicit    CustomWebView (QWidget* parent); 

        QWebView  * createWindow  (QWebPage::WebWindowType type)    override;
        void        closeEvent    (QCloseEvent            * event)  override;
    };
    
    /** QtWinUIApp is Qt application main window
        It expects for 2 HTML documents in applicaton resources:
        - "splash" page showing while Django server is starting (IDR_HTML_START)
        - page with collected messages showing in error case (IDR_HTML_REPORT)

        If _DEBUG is defined there are StringList with currently collected log messages showing in separate window and 
        QWebInspector for loaded into mWebView page 

    */
    struct QtWinUIApp : public QApplication
    {
        QMainWindow   mMainWindow;          ///< GUI
        CustomWebView mWebView;             ///< Qt browser
        QProcess      mZooProcess;          ///< holds running web server
        QString       mSelfHost;            ///< where we was started 
        #ifdef  _DEBUG
          QDialog   * mDlg;
        #endif  //_DEBUG
      public:
                      QtWinUIApp          ( int                       & argc,
                                            char                      **argv,
                                            int                         flags = ApplicationFlags);
                      ~QtWinUIApp         ( );

        void          runServerAndWaitPort( );
        void          showReportPage      ( );

        void          goToURL             ( QUrl const                & url);
        void          setWindowTitle      ( QString const             & title);
        void          resize              ( QSize const               & size);

        ///collects Qt's logging into our infrastructure
        static void   qtMessageCatcher    ( QtMsgType                   type,
                                            QMessageLogContext const  & context,
                                            QString const             & msg);

      protected:
        void          runServer           ( );
        bool          doesServiceExist    ( QString const             & server,
                                            int                         port,
                                            Milliseconds                connectTimeOut);
        bool          waitPort            ( QString const             & server,
                                            int                         port);
        void          slotLinkClicked     ( const QUrl                & url);
        bool          eventFilter         ( QObject                   * obj, 
                                            QEvent                    * event);
  };
}