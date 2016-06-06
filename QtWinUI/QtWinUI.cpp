// QtWinUI.cpp : Defines the entry point for the application.
//

#include "stdafx.h"
#include "QtWinUI.h"
#include "zoo_version.h"

#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <sstream>

#include <boost/iostreams/stream.hpp>
#include <boost/iostreams/stream_buffer.hpp>
#include <boost/iostreams/device/back_inserter.hpp>
#include <boost/iostreams/filtering_stream.hpp>

#include <QtCore/QUrl>
#include <QtCore/QStringList>
#include <QtCore/QStringListModel>
#include <QtCore/QProcessEnvironment>
#include <QtCore/QDir>
#include <QtCore/QTime>
#include <QtCore/QThread>
#include <QtCore/QRegExp>

#include <QtWidgets/QMessageBox>
#include <QtWidgets/QStyle>
#include <QtWidgets/QDesktopWidget>
#include <QtWidgets/QListView>
#include <QtWidgets/QVBoxLayout>

#include <QtGui/QResizeEvent>
#include <QtGui/QDesktopServices>

#include <QtWebKitWidgets/QWebInspector>
#include <QtWebKitWidgets/QWebFrame>

#include <QtNetwork/QTcpSocket>
#include <QtNetwork/QNetworkAccessManager>
#include <QtNetwork/QNetworkRequest>
#include <QtNetwork/QNetworkReply>

#define SET_QT_CONNECTION( x )  if ( !x ) throw std::runtime_error(#x)

using std::string;

namespace {
  using boottraper::Milliseconds;

  const QString       gApplicationName        = "Zoo";
  const QString       gOrganizationName       = "HeliconTech";
  const QString       gServer                 = "127.0.0.1";
  const int           gPort                   = 7799;
  const Milliseconds  gConnectTimeOut         = 15000;
  const Milliseconds  gWaitForConnected       = 500;
  const Milliseconds  gPingServerTimeOut      = 2;
  const QSize         gWindowSize             (1070, 752);
  const QUrl          gZoo_url                = "http://127.0.0.1:7799/";
  const QString       gZoo_version_url        = "static/zoo/version";

  string  getModuleFileName() {
    char            filePath [MAX_PATH];
    ::GetModuleFileNameA(nullptr, filePath, sizeof(filePath));
    return string(filePath);
  }

  QByteArray const getHtmlFromResource(int resID)  {
      HRSRC         hRes = FindResource(NULL, MAKEINTRESOURCE (resID), RT_HTML);
      HGLOBAL       hResourceLoaded = LoadResource(NULL, hRes);
      char const  * lpResLock = (char const *) LockResource(hResourceLoaded);
      DWORD         dwSizeRes = SizeofResource(NULL, hRes);

      return QByteArray(lpResLock, dwSizeRes);
  }

  bool  isVersionStr(QString const &version, int * major = NULL, int * minor = NULL, int * build = NULL) {
      QRegExp       reVersion ("(\\d+)\\.(\\d+)\\.(\\d+).*");

      if (reVersion.exactMatch(version)) {
        QStringList captures = reVersion.capturedTexts();

        if (major)  *major = captures[1].toInt();
        if (minor)  *minor = captures[2].toInt();
        if (build)  *build = captures[3].toInt();

        return true;
      }

      return false;
  }

  bool  isAppropriateVersion(QString const &version) {
      int           majorThis, minorThis, buildThis;
      int           majorOther, minorOther, buildOther;

      if (    isVersionStr(ZOO_VERSION, &majorThis, &minorThis, &buildThis) 
          &&  isVersionStr(version, &majorOther, &minorOther, &buildOther) ) {

        return true; //(majorThis <= majorOther) && (minorThis <= minorOther) && (buildThis <= buildOther);
      }

      return false;
  }
}

namespace log_saver {
  namespace io = boost::iostreams;
  typedef string                    DataHolder;
  typedef io::filtering_ostream     LogCollector;

  DataHolder            gOutputCollector;
  LogCollector          gLogCollector (io::back_inserter(gOutputCollector));

  #ifdef  _DEBUG
    //It is used jointly with QListView in _tWinMain
    //http://stackoverflow.com/questions/5802313/qt4-qstringlistmodel-in-qlistview
    class StringList : public QStringListModel  {
    public:
      void append (const QString& string){
        insertRows(rowCount(), 1);
        setData(index(rowCount()-1), string);
      }
      StringList& operator<<(const QString& string){
        append(string);
        return *this;
      }
    };

    StringList          gLogStringList;
    QStringListModel  & gLogStringsInstance = gLogStringList; //for external references like: namespace log_saver { extern QStringListModel & gLogStringsInstance; }

    #define             LOG_DEBUG(x)    log_saver::gLogStringList << x
  #else
    #define             LOG_DEBUG(x)
  #endif  //_DEBUG


  enum StdStream {
    StdOut, StdErr, Std_LAST_NO
  };

  enum KeyString {
    KeyStr_None, KeyStr_Error
  };

  const string          gStreamTitles[Std_LAST_NO] = {"stdout: ", "stderr: "};
  const string          gKeyStrings[] = {"Fatal Python error"};

  KeyString process(StdStream stdStream, QByteArray data) {
      QString     str(data);
      string      msg = (str += "\n").toStdString();

      //OutputDebugStringA(msg.c_str());
      gLogCollector << msg;
      qDebug() << gStreamTitles[stdStream].c_str() << str;

      if (stdStream == StdErr) {
        for(size_t i = 0; i < sizeof(gKeyStrings)/sizeof(gKeyStrings[0]); ++i)
          if (msg.find(gKeyStrings[i]) != string::npos)
            return KeyStr_Error;
      }

      return KeyStr_None;
  }
}

namespace boottraper {
  void showMessageAndThrowException(QString message, bool throwException = true) {
    QMessageBox msgBox;

    msgBox.setText(message);
    msgBox.exec();

    QByteArray      msg = message.toHtmlEscaped().toLocal8Bit();
    log_saver::gLogCollector << msg.constData() << "\n";
    LOG_DEBUG(msg.constData());

    if ( throwException )
      throw std::runtime_error (message.toStdString());
    //Application.Exit();
  }

  void showMessageAndThrowException(string message) {
    showMessageAndThrowException (QString (message.c_str()));
  }

  void showMessageAndThrowException(char const * message) {
    showMessageAndThrowException (QString (message));
  }

#ifdef ENABLED_JS_LOGGING
  //------------------------------------------CustomWebPage
  struct CustomWebPage : public QWebPage {
    CustomWebPage(QObject * parent) : QWebPage(parent) {
    }

    ~CustomWebPage() {
    }

    void triggerAction(WebAction action, bool checked) override {
      qDebug() << "triggerAction: " << action << ", checked=" << checked;
    }

    void    javaScriptConsoleMessage(const QString & message, int lineNumber, const QString & sourceID) override {
      log_saver::gLogStringList << message;
    }
  };
#endif // ENABLED_JS_LOGGING

  //------------------------------------------CustomWebView
  CustomWebView::CustomWebView(QWidget* parent) 
                : QWebView(parent)
  {
#ifdef ENABLED_JS_LOGGING
    setPage (new CustomWebPage(this));
#endif // ENABLED_JS_LOGGING
  }

  QWebView *CustomWebView::createWindow(QWebPage::WebWindowType type) {
      (void)type;
      CustomWebView * webView = new CustomWebView(this);

      webView->settings()->setAttribute(QWebSettings::JavascriptCanOpenWindows, true);
      webView->settings()->setAttribute(QWebSettings::LocalContentCanAccessRemoteUrls, true);
      webView->page()->setLinkDelegationPolicy(QWebPage::DelegateAllLinks);

      webView->setWindowFlags(Qt::Window);
      webView->show();
      return webView;
  }

  void CustomWebView::closeEvent(QCloseEvent *event) {
    page()->mainFrame()->evaluateJavaScript("console.debug('CustomWebView::closeEvent'); Console.cancel();");
    delete page();
    event->accept();
  }

  //------------------------------------------QtWinUIApp
  QtWinUIApp::QtWinUIApp(int &argc, char **argv, int flags)
                        : QApplication(argc, argv, flags)
                        , mMainWindow()
                        , mWebView(&mMainWindow)
                        , mZooProcess(static_cast<QWidget*>(&mMainWindow))
  {
    QString         startPage (getHtmlFromResource(IDR_HTML_START));
    QApplication  * app = static_cast<QApplication*> (this);
    const QObject * self = static_cast<const QObject *>(app);

    mWebView.page()->setLinkDelegationPolicy(QWebPage::DelegateExternalLinks);
    mWebView.settings()->setAttribute(QWebSettings::JavascriptCanOpenWindows, true);
    mWebView.settings()->setAttribute(QWebSettings::LocalContentCanAccessRemoteUrls, true);
    
    SET_QT_CONNECTION (connect(mWebView.page(), &QWebPage::linkClicked, this, &QtWinUIApp::slotLinkClicked));
    mMainWindow.installEventFilter(this);

    mWebView.setHtml(startPage);
    mWebView.show();
    mMainWindow.show();

    #ifdef  _DEBUG
      mDlg = new QDialog(&mMainWindow);
      mDlg->setWindowTitle("Web inspector view");
      QWebInspector *i = new QWebInspector(&mMainWindow);
      mWebView.settings()->setAttribute(QWebSettings::DeveloperExtrasEnabled, true);
      i->setPage(mWebView.page());
      mDlg->resize(600, 700);   
      mDlg->move(5, 350);
      mDlg->setLayout(new QVBoxLayout());
      mDlg->layout()->addWidget(i);
      mDlg->setModal(false);
      mDlg->show();
      mDlg->raise();
      mDlg->activateWindow();
    #endif  //_DEBUG
  }

  QtWinUIApp::~QtWinUIApp() {
    try {
      if (mZooProcess.state() != QProcess::NotRunning)
        mZooProcess.terminate();
        //mZooProcess.kill();
    }
    catch(...) {
      //do nothing
    }
  }

  bool QtWinUIApp::eventFilter(QObject *obj, QEvent *event) {
    if (event->type() == QEvent::Resize) {
        QResizeEvent *resizeEvent = static_cast<QResizeEvent*>(event);
        mWebView.resize (resizeEvent->size());
    } 

    return mMainWindow.eventFilter(obj, event);
  }

  void QtWinUIApp::setWindowTitle ( QString const & title) {
    mMainWindow.setWindowTitle(title);
  }

  void QtWinUIApp::resize ( QSize const & size) {
    mMainWindow.resize(size);
    mMainWindow.setGeometry(QStyle::alignedRect(Qt::LeftToRight, Qt::AlignCenter, mMainWindow.size(), desktop()->availableGeometry()));

    mWebView.resize(mMainWindow.size());
  }

  void QtWinUIApp::slotLinkClicked(const QUrl&url) {
    if (mSelfHost == url.host())
      mWebView.load(url);
    else
      QDesktopServices::openUrl(url);
  }

  void QtWinUIApp::showReportPage() {
    QString     reportPage (getHtmlFromResource(IDR_HTML_REPORT));

    log_saver::gLogCollector.flush();
    reportPage = reportPage.arg(log_saver::gOutputCollector.c_str());

    mWebView.setHtml(reportPage);
  }

  void QtWinUIApp::goToURL(QUrl const & url) {
      mSelfHost = url.host();
      mWebView.load(url);
  }

  void QtWinUIApp::runServer() {
    QProcessEnvironment env(QProcessEnvironment::systemEnvironment());
    QStringList         args;
    QString             path = env.value("PATH");
    QString             cmd = "zoocmd.exe";

    args <<"--run-server";//<<" --run-server-addr 7799 "<<"--log-level debug";

    SET_QT_CONNECTION ((mZooProcess.connect (&mZooProcess, &QProcess::readyReadStandardOutput, [=] () { log_saver::process(log_saver::StdOut, mZooProcess.readAllStandardOutput()); })));
    SET_QT_CONNECTION ((mZooProcess.connect (&mZooProcess, &QProcess::readyReadStandardError, [=] ()  { 
        log_saver::KeyString    result = log_saver::process(log_saver::StdErr, mZooProcess.readAllStandardError());
        if (result == log_saver::KeyStr_Error)
          mZooProcess.kill();
    })));

    mZooProcess.setProcessEnvironment(env);

    qDebug() << "runServer: start '" << cmd << "' with args '" << args << "'";

    mZooProcess.start(cmd, args, QIODevice::ReadOnly);
    if (mZooProcess.error() == QProcess::FailedToStart)
      showMessageAndThrowException(QString("Could not start Zoo server: ") + mZooProcess.errorString());
  }

  bool QtWinUIApp::waitPort(QString const & server, int port) {
    while (!doesServiceExist(server, port, gConnectTimeOut)) {
      if (mZooProcess.state() == QProcess::NotRunning)
        return false; //fail
    }

    return true;// OK
  }

  bool QtWinUIApp::doesServiceExist(QString const & server, int port, Milliseconds connectTimeOut) {
    try {
      QTcpSocket  client;
      bool        ok = false;

      qDebug() << "doesServiceExist: connectToHost(" << server << ", " << port << ")\n" ;
      client.connectToHost(server, port);
      processEvents();

      for (QTime time = QTime::currentTime(); time.msecsTo(QTime::currentTime()) < connectTimeOut; processEvents()) {
        QAbstractSocket::SocketState state = client.state();

        if ((ok = (state == QAbstractSocket::ConnectedState)) == true)
          break;

        QThread::msleep(gWaitForConnected);
        qDebug() << "doesServiceExist: waitForConnected() " << QTime::currentTime() << "\n";

        if ((connectTimeOut != gPingServerTimeOut) && (mZooProcess.state() == QProcess::NotRunning))
          break;
      }

      qDebug() << "doesServiceExist: ok=" << ok << "\n";

      client.close();
      return ok;
    }
    catch (...) {
      return false; //FAIL
    }
  }

  void QtWinUIApp::runServerAndWaitPort() {
    processEvents();

    if (doesServiceExist(gServer, gPort, gPingServerTimeOut)) {
      QUrl                  url;
      QNetworkAccessManager manager;
      QString               version;
      bool                  done = false;

      url = gZoo_url.toString() + gZoo_version_url;
      qDebug() << "Ask '" << url << "' for version\n";

      manager.get(QNetworkRequest(url));

      SET_QT_CONNECTION ((manager.connect (&manager, &QNetworkAccessManager::finished, 
          [&version, &done] (QNetworkReply *reply) 
      { 
        version = QString::fromUtf8(reply->readAll()).trimmed(); 
        done = true;
        qDebug() << "got version '" << version << "', our version '" << ZOO_VERSION << "'\n";
      })));
      
      for (QTime time = QTime::currentTime(); time.msecsTo(QTime::currentTime()) < gWaitForConnected; processEvents()) {
        processEvents();
      }

      if (!isVersionStr(version)) {
        showMessageAndThrowException(gZoo_url.toDisplayString() + " is not available.");
        return;
      }

      if (isAppropriateVersion (version)) {
        qDebug() << "will use running server\n";
        goToURL(gZoo_url);
        return;
      }

      showMessageAndThrowException("There is running zoo server " + version + " on " + gZoo_url.toDisplayString() + ". Please upgrade it to " ZOO_VERSION ".");
      return;
    }

    processEvents();
    runServer();

    if (!waitPort(gServer, gPort)) {
      showMessageAndThrowException("Zoo server closed unexpectedly");
      return;
    }

    goToURL(gZoo_url);
  }

  void QtWinUIApp::qtMessageCatcher(QtMsgType type, const QMessageLogContext &context, const QString &msg) {
      QByteArray          localMsg = msg.toLocal8Bit();
      std::stringstream   buf;

      switch (type) {
        case QtDebugMsg:      buf << "Debug"; break;
        case QtWarningMsg:    buf << "Warning"; break;
        case QtCriticalMsg:   buf << "Critical"; break;
        case QtFatalMsg:      buf << "Fatal"; break;
                              //abort();
      }

      buf << ": " << localMsg.constData() << " [" << context.file << ":" << context.line << ", " << context.function << "]";
      OutputDebugStringA (buf.str().c_str());
      log_saver::gLogCollector << buf.str() << "\n";
      LOG_DEBUG(buf.str().c_str());
  }
} //namespace boottraper

using namespace boottraper;

int APIENTRY _tWinMain(HINSTANCE /*hInstance*/, HINSTANCE /*hPrevInstance*/, LPTSTR lpCmdLine, int /*nCmdShow*/) {
  string          args(lpCmdLine, lpCmdLine + wcslen(lpCmdLine));
  int             argc = args.empty() ? 1 : 2;
  string          moduleFilename = getModuleFileName();
  char const    * argv[] = {moduleFilename.c_str(), args.c_str()};
  QStringList     libraryPaths ("plugins");

  SetErrorMode(SEM_FAILCRITICALERRORS); //Prevent Windows' error message boxes like "Drive not ready"

  qInstallMessageHandler(QtWinUIApp::qtMessageCatcher);
  QCoreApplication::setLibraryPaths (libraryPaths);

  QtWinUIApp      app(argc, const_cast<char**>(argv));
  QListView       listView;

  try {
    #ifdef  _DEBUG
      listView.move(10, 10);
      listView.resize(600, 300);
      listView.setModel(&log_saver::gLogStringList);
      listView.setFont (QFont("Courier New"));
      listView.show();
    #endif  //_DEBUG

    app.setApplicationName(gApplicationName);
    app.setWindowTitle(gApplicationName);
    app.setOrganizationName(gOrganizationName);

    app.resize(gWindowSize);

    app.runServerAndWaitPort();

    return app.exec();
  }
  catch (std::exception const &ex) {    //TODO: how to use "ex"?
    app.showReportPage();
    app.exec();
  }

  return 3;
}
