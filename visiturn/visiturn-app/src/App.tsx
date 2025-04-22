import React, { useEffect, useRef } from "react";

import logo from "./logo.svg";
import "./App.css";

// import { hot } from "react-hot-loader/root";
// import Map from "./components/map";
import MapContainer from "./MapContainer";
import * as amplitude from "@amplitude/analytics-browser";
import NoCrashIcon from "@mui/icons-material/NoCrash";
import CopyAllIcon from "@mui/icons-material/CopyAll";
import IconButton from "@mui/material/IconButton";
import FormControlLabel from "@mui/material/FormControlLabel";

// import * as React from "react";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import List from "@mui/material/List";
import Divider from "@mui/material/Divider";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import InboxIcon from "@mui/icons-material/MoveToInbox";
import MailIcon from "@mui/icons-material/Mail";

import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";
import FormHelperText from "@mui/material/FormHelperText";
import Input from "@mui/material/Input";
import Button from "@mui/material/Button";

// import { Table, Column, HeaderCell, Cell } from "rsuite-table";
// import "rsuite-table/lib/less/index.less"; // or 'rsuite-table/dist/css/rsuite-table.css'
import EnhancedTable from "./EnhancedTable";
import { Data } from "./EnhancedTable";

import Switch from "@mui/material/Switch";
import TextField from "@mui/material/TextField";
// import Input from "@mui/material/Input";

amplitude.init("d6fbe28f1b2bb2f937ca80859d58424c");
declare global {
    interface Window {
        kakao: any;
    }
}
// const App = (): JSX.Element => <Map />;
interface CsvModalProps {
    value: string;
    isOpen: boolean;
    // onOpen: boolean;
    onClose: any;
}

type Anchor = "top" | "left" | "bottom" | "right";
const emptyTable: Data[] = {} as Data[];

function App() {
    const [drivers, setDrivers] = React.useState("0");
    const [value, setValue] = React.useState("");
    const [dcsv, setDcsv] = React.useState("");
    const [routeSum, setDrawer] = React.useState(emptyTable);
    const [showInfo, setShowInfo] = React.useState(false);
    const [childRendered, setChildRendered] = React.useState(false);
    const [vnum, setVnum] = React.useState("0");
    // const { isOpen, onOpen, onClose } = useDisclosure();
    const [placement, setPlacement] = React.useState("right");

    const handleDriverNumberChange = (e: any) => {
        e.preventDefault();
        setVnum(drivers);
        console.log("drivers", drivers);
    };

    const handleInputChange = (e: any) => {
        let inputValue = e.target.value;
        setValue(inputValue);
        amplitude.track("addr_data_changed:" + inputValue);
    };

    const handleSwitchChange = (e: any) => {
        let inputValue = e.target.checked;
        // console.log("handleSwitchChange", inputValue, e.target);
        setShowInfo(inputValue);
        amplitude.track("x_switch_clicked:" + inputValue);
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(dcsv);
    };

    let handleRenderingChange = (isRendered: boolean) => {
        // const scheduleBttn = document.getElementById(
        //     "do_schedule"
        // ) as HTMLInputElement;
        setChildRendered(isRendered);
        setDrivers("0");
        setVnum("0");
        // if (!childRendered) {
        //     // if (!isRendered) {
        //     scheduleBttn.setAttribute("disabled", "true");
        // } else {
        //     scheduleBttn.removeAttribute("disabled");
        // }
        console.log("handleRenderingChange : chilRendered?", childRendered, "isRendered?", isRendered);
    };

    // let myRef = useRef(null);

    const [state, setState] = React.useState({
        top: false,
        left: false,
        bottom: false,
        right: false,
    });

    const toggleDrawer = (anchor: Anchor, open: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => {
        if (event.type === "keydown" && ((event as React.KeyboardEvent).key === "Tab" || (event as React.KeyboardEvent).key === "Shift")) {
            return;
        }

        setState({ ...state, [anchor]: open });
    };

    const list = (anchor: Anchor) => (
        <Box
            sx={{
                width: anchor === "top" || anchor === "bottom" ? "auto" : 250,
            }}
            role="presentation"
            onClick={toggleDrawer(anchor, false)}
            onKeyDown={toggleDrawer(anchor, false)}
        >
            <List>
                {["Inbox", "Starred", "Send email", "Drafts"].map((text, index) => (
                    <ListItem key={text} disablePadding>
                        <ListItemButton>
                            <ListItemIcon>{index % 2 === 0 ? <InboxIcon /> : <MailIcon />}</ListItemIcon>
                            <ListItemText primary={text} />
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
            <Divider />
            <List>
                {["All mail", "Trash", "Spam"].map((text, index) => (
                    <ListItem key={text} disablePadding>
                        <ListItemButton>
                            <ListItemIcon>{index % 2 === 0 ? <InboxIcon /> : <MailIcon />}</ListItemIcon>
                            <ListItemText primary={text} />
                        </ListItemButton>
                    </ListItem>
                ))}
            </List>
        </Box>
    );

    useEffect(() => {
        // handleRenderingChange(childRendered);
        // const input = document.getElementById("num_drivers") as HTMLInputElement;
        // input.value = "3";
    }, []);

    return (
        <div className="App">
            {/* <Button colorScheme="blue" onClick={onOpen}>
                +
            </Button>
             */}
            {(["top"] as const).map((anchor) => (
                <React.Fragment key={anchor}>
                    <IconButton aria-label="NoCrash" onClick={toggleDrawer(anchor, true)}>
                        <NoCrashIcon fontSize="small" />
                    </IconButton>
                    <IconButton aria-label="CopyAll" color="primary" onClick={handleCopy}>
                        <CopyAllIcon fontSize="small" />
                    </IconButton>
                    <Drawer anchor={anchor} open={state[anchor]} onClose={toggleDrawer(anchor, false)}>
                        <EnhancedTable route_info={routeSum} />
                        {/* {list(anchor)} */}
                    </Drawer>
                </React.Fragment>
            ))}
            <Box>
                <Stack direction="column" alignItems="stretch">
                    <Stack direction="row" alignItems="stretch" sx={{ margin: 0, padding: 0 }}>
                        <TextField
                            multiline
                            fullWidth
                            rows={4}
                            disabled={false}
                            placeholder="넘기기,순서,배송/수거,사이즈,색상,두께,고객 KEY,휴대폰 번호,지역,배송지 주소,비밀번호,구성품 을 탭으로 분리된 문자열로 넣어주세요."
                            value={value}
                            margin="dense"
                            inputProps={{
                                style: {
                                    fontSize: 10,
                                    lineHeight: 1,
                                    height: 100,
                                },
                            }}
                            sx={{
                                margin: 0,
                                padding: 0,
                            }}
                            onChange={handleInputChange}
                        />
                        <TextField
                            multiline
                            fullWidth
                            rows={4}
                            disabled={true}
                            value={dcsv}
                            margin="dense"
                            inputProps={{
                                style: {
                                    fontSize: 10,
                                    lineHeight: 1,
                                    height: 100,
                                },
                            }}
                            sx={{
                                margin: 0,
                                padding: 0,
                            }}
                            // isDisabled={true}
                            // onChange={handleInputChange}
                        />
                    </Stack>
                    <Stack direction="row" justifyContent="space-between">
                        <Stack spacing={1} direction="row" justifyContent="left">
                            <Button variant="contained" color="error" onClick={handleInputChange}>
                                입력 내용 지우기
                            </Button>
                            <FormControlLabel
                                control={
                                    <Switch
                                        id="allinfo"
                                        // size="small"
                                        color="secondary"
                                        onChange={handleSwitchChange}
                                        // checked={showInfo}

                                        // onChange={(e) => setShowInfo(e.target.value)}
                                    />
                                }
                                label="전체 정보 보이기"
                                labelPlacement="start"
                                sx={{
                                    "& .MuiFormControlLabel-label": {
                                        color: "purple",
                                        // fontSize: "1.5rem",
                                        // width: 300,
                                        // backgroundColor: "rgba(0,0,0,0.1)",
                                    },
                                }}
                            />
                        </Stack>
                        <Stack spacing={1} direction="row" justifyContent="right">
                            {/* <form onSubmit={handleDriverNumberChange}> */}

                            <FormControlLabel
                                control={
                                    <>
                                        <Input
                                            id="num_drivers"
                                            required
                                            type="string"
                                            value={drivers}
                                            // defaultValue={drivers}
                                            placeholder="운행 예상 차량 갯수입력"
                                            onChange={(event) => setDrivers(event.target.value)}
                                            sx={{
                                                width: 88,
                                                color: "#0288d1",
                                                marginLeft: 2,
                                                marginRight: 2,
                                            }}
                                        />
                                    </>
                                }
                                label="운행가능 차량수 : "
                                labelPlacement="start"
                                sx={{
                                    width: 280,

                                    "& .MuiFormControlLabel-label": {
                                        color: "#0288d1",
                                        // fontSize: "1.5rem",
                                        // backgroundColor: "rgba(0,0,0,0.1)",
                                    },
                                }}
                            />
                            <Button id="do_schedule" disabled={childRendered} color="primary" variant="contained" onClick={handleDriverNumberChange}>
                                배차 및 경로추천
                            </Button>
                            {/* </form> */}
                        </Stack>
                    </Stack>
                    <Stack>
                        <MapContainer
                            addrList={value}
                            showPanel={showInfo}
                            numDrivers={vnum}
                            disableVrpButton={handleRenderingChange}
                            setToTextArea={setDcsv}
                            setToDrawer={setDrawer}
                        />
                    </Stack>
                </Stack>
            </Box>
        </div>
    );
}
export default App;
